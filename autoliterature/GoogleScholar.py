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
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
    
    def set_proxy(self, proxy_name = "free", proxy_address = "173.192.21.89:80", use_proxy=False):
        """set proxy handler
        
        Aargs: 
            proxy (str): proxy (str): The proxy adress. e.g 127.0.1:1123
            
        Returns:
            A proxy handler object.
        """
        if use_proxy:
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
        pubs_iter = scholarly.search_pubs(item)
        dictinfo = next(pubs_iter)
        logger.info(dictinfo)
        bib_dict = {
            "title": dictinfo['bib']['title'],
            "author": ' and '.join(dictinfo['bib']['author']),
            "journal": dictinfo['bib']['venue'],
            "year": dictinfo['bib']['pub_year'],
            "url": dictinfo['pub_url'],
            "pdf_link": dictinfo['eprint_url'],
            "cited_count": dictinfo['num_citations']
        }
        
        return bib_dict


    # def get_info_by_arxivid(self, arxivId, handler=False):
    #     """Get the meta information by the given paper arxiv_id. 
        
    #     Args:
    #         doi (str): The arxiv Id
    #         handler (handler object): use proxy
            
    #     Returns:
    #         A dict containing the paper information. 
    #         {
    #             "title": xxx,
    #             "author": xxx,
    #             "journal": xxx,
    #             etc
    #         } 
    #         OR
    #         None
    #     """
        
    #     params = "?search_query=id:"+quote(unidecode(arxivId))
        
    #     try:
    #         if handler:
    #             result = feedparser.parse(self.base_url + params, handlers=[handler])
    #         else:
    #             result = feedparser.parse(self.base_url  + params)
    #         items = result.entries

    #         item = items[0]
    #         if "arxiv_doi" in item:
    #             doi = item["arxiv_doi"]
                
    #             crossref_info = crossrefInfo()
    #             if handler:
    #                 crossref_info.set_proxy(proxy=handler.proxies["http"].split('//')[-1])
    #             return crossref_info.get_info_by_doi(doi)
    #         else:
    #             return self.extract_json_info(item)
    #     except:
    #         logger.error("DOI: {} is error.".format(arxivId))
            
    
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