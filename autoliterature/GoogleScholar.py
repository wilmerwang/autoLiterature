import logging
import requests 
from urllib.request import ProxyHandler
import feedparser
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from unidecode import unidecode

import json
from scholarly import scholarly, ProxyGenerator


logging.basicConfig()
logger = logging.getLogger('GoogleScholar')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class GscholarInfo(object):
    
    def set_proxy(self, proxy_name = "free", proxy_address = None):
        """set proxy handler
        
        Aargs: 
            proxy (str): proxy (str): The proxy adress. e.g 127.0.1:1123
            
        Returns:
            A proxy handler object.
        """
        # TODO find a better proxy strategy
        if proxy_address:
            sucess = False
            pg = ProxyGenerator()
            if proxy_name == "free":
                sucess = pg.FreeProxies()
            elif proxy_name == "single":
                sucess = pg.SingleProxy(http = proxy_address, https = proxy_address)
            logger.info(f'Proxy setup sucess: {sucess}.')
            scholarly.use_proxy(pg)
            
    
    def extract_json_info(self, item):
        """Extract bib json information from requests.get().json()
        
        Args:
            item (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
        bib_dict = None
        trial_num = 0
        
        while trial_num<10:
            try:
                trial_num+=1
                pubs_iter = scholarly.search_pubs(item)
                dictinfo = next(pubs_iter)
                # logger.info(dictinfo)
                bib_dict = {
                    "title": dictinfo['bib']['title'].replace('\n', ''),
                    "author": ' and '.join(dictinfo['bib']['author']),
                    "journal": dictinfo['bib']['venue'],
                    "year": dictinfo['bib']['pub_year'],
                    "url": dictinfo['pub_url'],
                    "pdf_link": dictinfo['eprint_url'],
                    "cited_count": dictinfo['num_citations']
                }
                break
            except:
                pass
        
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
    arxivId = "2208.05623"
    title = "Heterogeneous Graph Attention Network"
    
    gscholar_info = GscholarInfo()
    gscholar_info.set_proxy(proxy_name='single')
    
    bib_arxiv = gscholar_info.get_info_by_title(title)
    # bib_title = arxiv_info.get_info_by_title(title)
    
    print(bib_arxiv)
    print("\n")
    # print(bib_title)