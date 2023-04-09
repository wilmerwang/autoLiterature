import logging
import requests 
from urllib.request import ProxyHandler
import feedparser
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from unidecode import unidecode

import dblp
import pandas as pd


logging.basicConfig()
logger = logging.getLogger('DBLP')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class DBLPInfo(object):
    
    def set_proxy(self, proxy_address = None):
        """set proxy handler
        
        Aargs: 
            proxy (str): proxy (str): The proxy adress. e.g 127.0.1:1123
            
        Returns:
            A proxy handler object.
        """
        pass
            
    
    def extract_json_info(self, item):
        """Extract bib json information from requests.get().json()
        
        Args:
            item (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
        trial_num = 0
        while trial_num<10:
            trial_num+=1
            try:
                results = dblp.search([item])
                break
            except:
                if trial_num == 10:
                    results = pd.DataFrame({'A' : []})
                else:
                    pass
        
            
        
        if not results.empty:
            bib_dict = {
                "title": str(results['Title'][0]),
                "author": ' and '.join([str(Entry) for Entry in results['Authors'][0]]),
                "journal": str(results['Where'][0]),
                "year": str(results['Year'][0]),
                "url": str(results['Link'][0]),
                "pdf_link": None,
                "cited_count": None
            }
        else: 
            bib_dict = None
        return bib_dict
            
    
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
        return self.extract_json_info(title)
            
            
if __name__ == "__main__":
    # arxivId = "2208.05623"
    # title = "Heterogeneous Graph Attention Network"
    
    # gscholar_info = GscholarInfo()
    # gscholar_info.set_proxy(proxy_name='single')
    
    # bib_arxiv = gscholar_info.get_info_by_title(title)
    # # bib_title = arxiv_info.get_info_by_title(title)
    
    # print(bib_arxiv)
    # print("\n")
    # # print(bib_title)
    results = dblp.search(["Finetunedlanguage models are zero-shot learners"])

    print(results)