import logging
import requests 
from urllib.request import ProxyHandler
import feedparser
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote
from unidecode import unidecode

from .crossref import crossrefInfo


logging.basicConfig()
logger = logging.getLogger('arxiv')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class arxivInfo(object):
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
    
    def set_proxy_handler(self, proxy):
        """set proxy handler
        
        Aargs: 
            proxy (str): proxy (str): The proxy adress. e.g 127.0.1:1123
            
        Returns:
            A proxy handler object.
        """
        proxy_handler = ProxyHandler({"http": f"http://{proxy}",
                                      "https": f"https://{proxy}"})
        return proxy_handler
            
    
    def extract_json_info(self, item):
        """Extract bib json information from requests.get().json()
        
        Args:
            item (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
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
            "title": title,
            "author": authors,
            "journal": journal,
            "year": year,
            "url": paper_url,
            "pdf_link": item.link.replace("abs", "pdf")+".pdf",
            "cited_count": None
        }
        
        return bib_dict


    def get_info_by_arxivid(self, arxivId, handler=False):
        """Get the meta information by the given paper arxiv_id. 
        
        Args:
            doi (str): The arxiv Id
            handler (handler object): use proxy
            
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
        
        params = "?search_query=id:"+quote(unidecode(arxivId))
        
        try:
            if handler:
                result = feedparser.parse(self.base_url + params, handlers=[handler])
            else:
                result = feedparser.parse(self.base_url  + params)
            items = result.entries

            item = items[0]
            if "arxiv_doi" in item:
                doi = item["arxiv_doi"]
                
                crossref_info = crossrefInfo()
                if handler:
                    crossref_info.set_proxy(proxy=handler.proxies["http"].split('//')[-1])
                return crossref_info.get_info_by_doi(doi)
            else:
                return self.extract_json_info(item)
        except:
            logger.error("DOI: {} is error.".format(arxivId))
            
    
    def get_info_by_title(self, title, field='ti'):
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
        params = "?search_query="+field+":"+quote(unidecode(title))
        url = self.base_url + params
        try:
            result = feedparser.parse(url)
            items = result.entries
            print(len(items))
            
            for i, item in enumerate(items):
                
                title_item = item.title
                try:
                    title_item = title_item.decode("utf-8")
                except:
                    pass
            
                item.title = title_item

                if title_item.lower() == title.lower():
                    return self.extract_json_info(item)
                
                items[i] = item

            return [self.extract_json_info(it) for it in items]
        except:
            logger.error("Title: {} is error.".format(title)) 
            
            
if __name__ == "__main__":
    arxivId = "2208.05623"
    title = "Heterogeneous Graph Attention Network"
    
    arxiv_info = arxivInfo()
    arxiv_info.set_proxy_handler(proxy="127.0.1:1123")
    
    bib_arxiv = arxiv_info.get_info_by_arxivid(arxivId)
    # bib_title = arxiv_info.get_info_by_title(title)
    
    print(bib_arxiv)
    print("\n")
    # print(bib_title)