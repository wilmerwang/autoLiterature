# -*- coding: utf-8 -*- 
import os 
import re 
import hashlib
import logging
import urllib3
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from urllib import parse

import feedparser
from unidecode import unidecode
import requests 
from bs4 import BeautifulSoup 
# import bibtexparser
from retrying import retry
import dropbox


# log config
logging.basicConfig()
logger = logging.getLogger('Sci-Hub')
logger.setLevel(logging.DEBUG)

urllib3.disable_warnings()
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class folderMoniter(object):
    def __init__(self, folder_path):
        self.folder_path = folder_path

        self.file_md5 = dict()

    def _files_in_folder(self):
        return [os.path.join(self.folder_path, p) for p in os.listdir(self.folder_path)]

    def file_md5_update(self):
        files = self._files_in_folder()

        added_files = list(set(files) - set(self.file_md5.keys()))
        self.file_md5.update(zip(added_files, [' ']*len(added_files)))

        removed_files = list(set(self.file_md5.keys()) - set(files))
        for removed_file in removed_files:
            del self.file_md5[removed_file]

        modified_items = dict()
        for file_path, md5_before in self.file_md5.items():
            md5_now = hashlib.md5(open(file_path).read().encode('utf-8')).hexdigest()
            if md5_now != md5_before:
                self.file_md5[file_path] = md5_now
                modified_items[file_path] = md5_now

        return modified_items 


class patternRecognizer(object):
    def __init__(self, regular_rule):
        self.pattern = re.compile(regular_rule)

    def match(self, string):
        return self.pattern.match(string)
    
    def findall(self, string):
        return self.pattern.findall(string)

    def multiple_replace(self, content, **replace_dict):
        def replace_(value):
            match = value.group()
            if match in replace_dict.keys():
                return replace_dict[match]
            else:
                return match+" **Not Correct, Check it**"
        
        replace_content = self.pattern.sub(replace_, content)
        
        return replace_content
        

class metaExtracter(object):
    def __init__(self):
        pass 

    def check_string(self, re_exp, str):
        res = re.search(re_exp, str)
        if res:
            return True
        else:
            return False

    def _classify(self, identifier):
        """
        Classify the type of identifier:
        arxivId - arxivId
        doi - digital object identifier
        """
        if self.check_string(r'10\.[0-9]{4}/.*', identifier):
            return 'doi'
        else:
            return 'arxivId'

    def doi2bib(self, doi):
        bare_url = "http://api.crossref.org/"
        # url = "{}works/{}/transform/application/x-bibtex"
        # TODO: url cannot return journal name
        url = "{}works/{}"
        url = url.format(bare_url, doi)
        
        try:
            r = requests.get(url)
            # found = False if r.status_code != 200 else True
            # bib = str(r.content, "utf-8")

            # if found:
            # bib_database = bibtexparser.loads(bib)
            # return bib_database.entries[0]
            bib = r.json()['message']
            pub_date = [str(i) for i in bib['published']["date-parts"][0]]
            pub_date = '-'.join(pub_date)

            authors = ' and '.join([i["family"]+" "+i['given'] for i in bib['author'] if "family" and "given" in i.keys()])

            if bib['short-container-title']:
                journal = bib['short-container-title'][0]
            else:
                journal = bib['container-title'][0]

            bib_dict = {
                "title": bib['title'][0],
                "author": authors,
                "journal": journal,
                "year": pub_date,
                "url": bib["URL"],
                "pdf_link": bib["link"][0]["URL"],
                "cited_count": bib["is-referenced-by-count"]
            }
            
            return bib_dict
        except:
            logger.info("DOI: {} is error.".format(doi))

    def arxivId2bib(self, arxivId):
        bare_url = "http://export.arxiv.org/api/query"

        params = "?search_query=id:"+quote(unidecode(arxivId))
        
        try:
            result = feedparser.parse(bare_url + params)
            items = result.entries
            # found = len(items) > 0

            item = items[0]
            # if found:
            if "arxiv_doi" in item:
                doi = item["arxiv_doi"]
                bib_dict = self.doi2bib(doi)
            else:
                paper_url = item.link 
                title = item.title
                journal = "arxiv"
                published = item.published.split("-")
                if len(published) > 1:
                    year = published[0]
                else: 
                    year = ' '
                
                authors = item.authors
                if len(authors) > 0:
                    first_author = authors[0]["name"].split(" ")
                    authors = " and ".join([author["name"] for author in authors])
                else:
                    first_author = authors
                    authors = authors

                bib_dict = {
                    "journal": journal,
                    "url": paper_url,
                    "title": title,
                    "year": year,
                    "author": authors,
                    "ENTRYTYPE": "article"
                }

            return bib_dict 
        except:
            logger.info("DOI: {} is error.".format(arxivId))

    def id2bib(self, identifier):
        id_type = self._classify(identifier)

        if id_type == "doi":
            bib_dict = self.doi2bib(identifier) 
        else:
            bib_dict = self.arxivId2bib(identifier) 

        return bib_dict


class urlDownload(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.available_base_url_list = self._get_available_scihub_urls()
        self.base_url = self.available_base_url_list[0] + '/'

    def _get_available_scihub_urls(self):
        '''
        Finds available scihub urls via https://lovescihub.wordpress.com/
        '''
        urls = []
        # res = requests.get('https://sci-hub.now.sh/')
        res = requests.get('https://lovescihub.wordpress.com/')
        s = self._get_soup(res.content)
        for a in s.find_all('a', href=True):
            if 'sci-hub.' in a['href']:
                urls.append(a['href'])
        return urls

    def _change_base_url(self):
        if not self.available_base_url_list:
            raise Exception('Ran out of valid sci-hub urls')
        del self.available_base_url_list[0]
        self.base_url = self.available_base_url_list[0] + '/'
        logger.info("I'm changing to {}".format(self.available_base_url_list[0]))


    def check_string(self, re_exp, str):
        res = re.search(re_exp, str)
        if res:
            return True
        else:
            return False

    # @retry(wait_random_min=100, wait_random_max=1000, stop_max_attempt_number=10)
    # def download(self, identifier, destination='', path=None):
    #     """
    #     Downloads a paper from sci-hub given an indentifier (DOI, PMID, URL).
    #     Currently, this can potentially be blocked by a captcha if a certain
    #     limit has been reached.
    #     """
    #     data = self.fetch(identifier)

    #     if not 'err' in data:
    #         self._save(data['pdf'],
    #                    os.path.join(destination, path if path else data['name']))

    #     return data

    def fetch(self, identifier):
        """
        Fetches the paper by first retrieving the direct link to the pdf.
        If the indentifier is a DOI, PMID, or URL pay-wall, then use Sci-Hub
        to access and download paper. Otherwise, just download paper directly.
        """
        try:
            url = self._get_direct_url(identifier)

            # verify=False is dangerous but sci-hub.io 
            # requires intermediate certificates to verify
            # and requests doesn't know how to download them.
            # as a hacky fix, you can add them to your store
            # and verifying would work. will fix this later.
            res = self.sess.get(url, verify=False)

            if res.headers['Content-Type'] != 'application/pdf':
                # self._change_base_url()
                logger.info('Failed to fetch pdf with identifier %s '
                                           '(resolved url %s) due to captcha' % (identifier, url))
            else:
                return {
                    'pdf': res.content,
                    'url': url
                }
        except:
            logger.info("")

    def _get_direct_url(self, identifier):
        """
        Finds the direct source url for a given identifier.
        """
        id_type = self._classify(identifier)

        if id_type == 'url-direct':
            return identifier
        elif id_type == 'arxivId':
            return "https://arxiv.org/pdf/" + identifier + ".pdf"
        else:
            return self._search_direct_url(identifier)

    def _search_direct_url(self, identifier):
        """
        Sci-Hub embeds papers in an iframe. This function finds the actual
        source url which looks something like https://moscow.sci-hub.io/.../....pdf.
        """
        res = self.sess.get(self.base_url + identifier, verify=False)
        s = self._get_soup(res.content)

        embed_names = ['iframe', 'embed']
        for embed_name in embed_names:
            iframe = s.find(embed_name)
            if iframe != None:
                break 

        if iframe.get('src').startswith('//'):
            return 'https:' + iframe.get('src')
        else:
            return iframe.get('src')

    def _classify(self, identifier):
        """
        Classify the type of identifier:
        url-direct - openly accessible paper
        url-non-direct - pay-walled paper
        pmid - PubMed ID
        doi - digital object identifier
        """
        if (identifier.startswith('http') or identifier.startswith('https')):
            if identifier.endswith('pdf'):
                return 'url-direct'
            else:
                return 'url-non-direct'
        elif identifier.isdigit():
            return 'pmid'
        elif self.check_string(r'10\.[0-9]{4}/.*', identifier):
            return 'doi'
        else:
            return 'arxivId'

    # def _save(self, data, path):
    #     """
    #     Save a file give data and a path.
    #     """
    #     with open(path, 'wb') as f:
    #         f.write(data)

    def _get_soup(self, html):
        """
        Return html soup.
        """
        return BeautifulSoup(html, 'html.parser')


class dropboxInteractor(object):
    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(access_token)

    def files_upload(self, file_, file_path, mode=dropbox.files.WriteMode.overwrite):
        self.dbx.files_upload(file_, file_path, mode=dropbox.files.WriteMode.overwrite)

    def generate_shared_url(self, file_path):
        shared_path = self.dbx.sharing_create_shared_link(file_path).url
        # shared_path = self.dbx.sharing_get_file_metadata(file_path).preview_url
        # shared_path = parse.unquote(shared_path)

        return shared_path

    def sharedlinks_files_list_folder(self, path):
        sharedlinks_files_dict = {}
        for entry in self.dbx.files_list_folder(path).entries:
            entry_path = entry.path_display
            # entry_shared_link = self.dbx.sharing_get_file_metadata(entry_path).preview_url
            entry_shared_link = self.dbx.sharing_create_shared_link(entry_path).url
            entry_shared_link = parse.unquote(entry_shared_link)
            
            sharedlinks_files_dict[entry_shared_link] = entry_path

        return sharedlinks_files_dict

    def del_file(self, path):
        self.dbx.files_delete_v2(path)


def note_modified(pattern_recog, md_file, **replace_dict):
    with open(md_file, 'r') as f:
        content = f.read()
    
    replaced_content = pattern_recog.multiple_replace(content, **replace_dict)

    with open(md_file, 'w') as f:
        f.write(''.join(replaced_content))


class attachRemove(object):
    def __init__(self, md_file, attach_path, dbx):
        self.files_sharedlinks_dict = dbx.sharedlinks_files_list_folder(attach_path)
        self.md_file = md_file
        self.dbx = dbx 

    def _pattern(self, pattern):
        return re.compile(pattern)

    def _removed_attachments(self, pattern):
        with open(self.md_file, 'r') as f:
            string = f.read()

        pattern_rec = self._pattern(pattern)
        
        m = pattern_rec.findall(string)

        removed_attachments = list(set(self.files_sharedlinks_dict.keys() - set(m)))

        for attach in removed_attachments:
            self.dbx.del_file(attach)

