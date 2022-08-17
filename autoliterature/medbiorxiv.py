import logging
import requests 
from bs4 import BeautifulSoup

from .crossref import crossrefInfo

logging.basicConfig()
logger = logging.getLogger('biorxiv')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class BMxivInfo(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.base_url = "https://api.biorxiv.org/details/"
        self.servers = ["biorxiv", "medrxiv"]
    
    
    def set_proxy(self, proxy=False):
        """set proxy for session
        
        Args:
            proxy (str): The proxy adress. e.g 127.0.1:1123
        Returns:
            None
        """
        if proxy:
            self.sess.proxies = {
                "http": proxy,
                "https": proxy, }
            
    
    def extract_json_info(self, item):
        """Extract bib json information from requests.get().json()
        
        Args:
            item (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
        paper_url = f"https://www.biorxiv.org/content/{item['doi']}"
        title = item["title"]
        journal = item["server"]
        published = item["date"].split('-')
        if len(published) > 1:
            year = published[0]
        else: 
            year = ' '

        authors = item['authors'].split("; ")
        if len(authors) > 0:
            authors = " and ".join([author for author in authors])
        else:
            authors = authors

        bib_dict = {
            "title": title,
            "author": authors,
            "journal": journal,
            "year": year,
            "url": paper_url,
            "pdf_link": f"{paper_url}.full.pdf",
            "cited_count": None
        }
        
        return bib_dict


    def get_info_by_bmrxivid(self, bmrxivid):
        """Get the meta information by the given paper biorxiv_id or medrxiv_id. 
        
        Args:
            doi (str): The biorxiv or medrxiv Id
            
        Returns:
            A dict containing the paper information. 
            {
                "title": xxx,
                "author": xxx,
                "journal": xxx,
                etc
            } 
            OR
            None
        """
        urls = [self.base_url + server + "/" + bmrxivid for server in self.servers]
        for url in urls:
            try:
                r = self.sess.get(url)

                bib = r.json()['collection'][-1]
                
                if "published" in bib.keys() and bib['published'] != "NA":
                    doi = bib["published"]
                    print(doi)
                    crossref_info = crossrefInfo()
                    if len(self.sess.proxies) > 0:
                        crossref_info.set_proxy(self.sess.proxies['http'].split('//')[-1])
                    return crossref_info.get_info_by_doi(doi)
                 
                return self.extract_json_info(bib)
                
            except:
                logger.error("DOI: {} is error.".format(bmrxivid)) 
            
    
    def get_info_by_title(self, title):
        """Get the meta information by the given paper title. 
        
        Args:
            doi (str): The paper title
            
        Returns:
            A dict containing the paper information. 
            {
                "title": xxx,
                "author": xxx,
                "journal": xxx,
                etc
            }
            OR
            None
            OR
            A list [{}, {}, {}]
        """
        base_url = "https://www.biorxiv.org/search/{}%20jcode%3Amedrxiv%7C%7Cbiorxiv%20numresults%3A25%20\sort%3Arelevance-rank%20\format_result%3Astandard"
        query = title.replace(' ', '%252B')
        
        url = base_url.format(query)
        try:
            result = self.sess.get(url)
            soup = BeautifulSoup(result.content, "lxml")
            soup_items = soup.find_all("div",class_="highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list clearfix")
            
            soup_dict = dict()
            for sp in soup_items:
                key = sp.find("a", class_="highwire-cite-linked-title").span.text
                value = sp.find("span", class_="highwire-cite-metadata-doi highwire-cite-metadata").text.split("org/")[-1].split("v")[0].replace(" ", "")
                soup_dict[key] = value
            
            for item_title, item_doi in soup_dict.items():
                try:
                    item_title = item_title.decode("utf-8")
                except:
                    pass

                if item_title.lower() == title.lower():
                    return self.get_info_by_bmrxivid(item_doi)

            return [self.get_info_by_bmrxivid(it) for it in soup_dict.values()]
        except:
            logger.error("Title: {} is error.".format(title)) 
            
            
if __name__ == "__main__":
    
    arxivId = "10.1101/2022.07.28.22277637"
    # title = "Oxygen restriction induces a viable but non-culturable population in bacteria"
    # title = "A molecular atlas of the human postmenopausal fallopian tube and ovary from single-cell RNA and ATAC sequencing"
    # title = "Radiographic Assessment of Lung Edema (RALE) Scores are Highly Reproducible and Prognostic of Clinical Outcomes for Inpatients with COVID-19"
    # title = "Untargeted metabolomics of COVID-19 patient serum reveals potential prognostic markers of both severity and outcome"
    
    arxiv_info = BMxivInfo()
    arxiv_info.set_proxy(proxy="127.0.1:1123")
    
    bib_arxiv = arxiv_info.get_info_by_bmrxivid(arxivId)
    # bib_title = arxiv_info.get_info_by_title(title)
    
    print(bib_arxiv)
    print("\n")
    # print(bib_title)