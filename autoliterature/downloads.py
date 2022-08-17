import logging
import re 
import os 

from .arxiv import arxivInfo
from .crossref import crossrefInfo
from .medbiorxiv import BMxivInfo
from .pdfs import pdfDownload

# log config
logging.basicConfig()
logger = logging.getLogger('Downloads')
logger.setLevel(logging.INFO)

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}



def check_string(re_exp, str):
    res = re.match(re_exp, str)
    if res:
        return True
    else:
        return False

def classify(identifier):
    """
    Classify the type of paper_id:
    arxivId - arxivId
    doi - digital object identifier
    medbiorxivId - medrxiv or biorxiv id
    title - title
    """
    if check_string(r'10\.(?!1101)[0-9]{4}/\.*', identifier):
        return 'doi'
    elif check_string(r'10\.1101/\.*', identifier):
        return "medbiorxivId"
    elif check_string(r'[0-9]{2}[0-1][0-9]\.[0-9]{3,}.*', identifier) or check_string(r'.*/[0-9]{2}[0-1][0-9]{4}', identifier):
        return 'arxivId'
    elif check_string(r'[a-zA-Z\d\.-/\s]*', identifier):
        return 'title'
    else:
        return "unrecognized"
    
def get_paper_info_from_paperid(paper_id, proxy=None):
    id_type = classify(paper_id)
    
    if id_type == "doi":
        downloader = crossrefInfo()
        if proxy:
            downloader.set_proxy(proxy=proxy)
        bib_dict = downloader.get_info_by_doi(paper_id)
        
    elif id_type == "arxivId":
        downloader = arxivInfo()
        if proxy:
            downloader.set_proxy_handler(proxy=proxy)
        bib_dict = downloader.get_info_by_arxivid(paper_id)
        
    elif id_type == "medbiorxivId":
        downloader = BMxivInfo()
        if proxy:
            downloader.set_proxy(proxy=proxy)
        bib_dict = downloader.get_info_by_bmrxivid(paper_id)

    elif id_type == "title":
        pass 
    else:
        pass 
    
    try:
        return bib_dict 
    except:
        pass 


def get_paper_pdf_from_paperid(paper_id, path, proxy=None, direct_url=None):
    pdf_downloader = pdfDownload()
    if proxy:
        pdf_downloader.set_proxy(proxy=proxy)
    
    if direct_url:
        content = pdf_downloader.get_pdf_from_direct_url(direct_url)
        if not content:
            content = pdf_downloader.get_pdf_from_sci_hub(paper_id)
    else:
        content = pdf_downloader.get_pdf_from_sci_hub(paper_id)
    
    try:
        if not os.path.exists(path.rsplit("/", 1)[0]):
            os.makedirs(path.rsplit("/", 1)[0])
        pdf_downloader._save(content['pdf'], path)
    except:
        pass 
    



if __name__ == "__main__":
    doi = "10.1016/j.wneu.2012.11.074"
    arxiv_id = "2208.05623"
    medbiorxiv_id = "10.1101/2022.07.28.22277637"
    undefine_name = "sjsldjfnadijjsl;kjdjf"
    
    print(get_paper_info_from_paperid(doi))
    print(get_paper_info_from_paperid(arxiv_id))
    print(get_paper_info_from_paperid(medbiorxiv_id))
    print(get_paper_info_from_paperid(undefine_name))