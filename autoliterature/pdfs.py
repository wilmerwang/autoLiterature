import logging
import requests 
from urllib.parse import urlunsplit, urlsplit
from bs4 import BeautifulSoup

logging.basicConfig()
logger = logging.getLogger('PDFs')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class pdfDownload(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        
    def set_proxy(self, proxy=None):
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
    
    
    def _get_available_scihub_urls(self):
        '''
        Finds available scihub urls via https://lovescihub.wordpress.com/ or 
        https://sci-hub.now.sh/
        '''
        urls = []
        res = self.sess.get('https://lovescihub.wordpress.com/')
        s = BeautifulSoup(res.content, 'html.parser')
        for a in s.find('div', class_="entry-content").find_all('a', href=True):
            if 'sci-hub.' in a['href']:
                urls.append(a['href'])
        return urls
    
        
    def fetch(self, url, auth=None):
        '''Fetch pdf
        
        Args:
            url (str):

        Returns:
            A dict OR None
        '''
        try:
            r = self.sess.get(url, auth=auth)
        
            if r.headers["Content-Type"] != "application/pdf":
                logger.info("Failed to fetch pdf with url: {}".format(url))
            else:
                return {
                    'pdf': r.content,
                    'url': url
                    }
        except:
            logger.error("Failed to open url: {}".format(url))
    
    
    def get_pdf_from_direct_url(self, url, auth=None):
        return self.fetch(url, auth=auth) 
    
    
    def get_pdf_from_sci_hub(self, identifier, auth=None):
        '''Fetch pdf from sci-hub based on doi or url
        
        Args: 
            identifier (str): DOI or url
            auth (tuple): ("user", "passwd")
        
        Returns:
            A dict OR None
        '''
        for base_url in self._get_available_scihub_urls():
            r = self.sess.get(base_url + '/' + identifier, auth=auth)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            pdf_div_names = ['iframe', 'embed']
            for pdf_div_name in pdf_div_names:
                pdf_div = soup.find(pdf_div_name)
                if pdf_div != None:
                    break 
            try:
                url_parts = urlsplit(pdf_div.get('src'))
                if url_parts[1]:
                    if url_parts[0]:
                        pdf_url = urlunsplit((url_parts[0], url_parts[1], url_parts[2], '', ''))
                    else:
                        pdf_url = urlunsplit(('https', url_parts[1], url_parts[2], '', ''))
                else:
                    pdf_url = urlunsplit(('https', urlsplit(base_url)[1], url_parts[2], '', ''))
                    
                return self.fetch(pdf_url, auth)
            except:
                pass
    
        logger.info("Failed to fetch pdf with all sci-hub urls")

    def _save(self, content, path):
        with open(path, "wb") as f:
            f.write(content)
            

if __name__ == "__main__":
    doi = "10.1145/3308558.3313562"
    
    pdf_download = pdfDownload()
    pdf_download.set_proxy("127.0.1:1123")
    
    pdf_dict = pdf_download.get_pdf_from_sci_hub(doi)
    if pdf_dict:
        print(pdf_dict['url'])
        pdf_download.download(pdf_dict['pdf'] ,"/home/admin/tmp.pdf")
        
    # pdf_dict2 = pdf_download.get_pdf_from_direct_url("https://arxiv.org/pdf/2208.05419.pdf")
    # if pdf_dict2:
    #     print(pdf_dict2['url'])
    #     pdf_download.download(pdf_dict2['pdf'] ,"/home/admin/tmp2.pdf")
    
    