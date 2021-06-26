# -*- coding: utf-8 -*- 
import os 
from urllib.parse import urlparse 

import requests 
from bs4 import BeautifulSoup 


def metadate_keys(path):
    site_name = urlparse(path).netloc
    
    keys_dict = dict()
    
    if site_name == "arxiv.org": 
        keys_dict['title'] = "citation_title"
        keys_dict['date'] = "citation_online_date" 
        keys_dict['publisher'] = "twitter:site"
        keys_dict['pdf_url'] = "citation_pdf_url"

    elif site_name == "www.nature.com":
        keys_dict['title'] = "citation_title"
        keys_dict['date'] = "citation_online_date" 
        keys_dict['publisher'] = "citation_journal_abbrev"
        keys_dict['pdf_url'] = "citation_pdf_url" 
        
    elif site_name == "ojs.aaai.org":
        keys_dict['title'] = "citation_title"
        keys_dict['date'] = "citation_date" 
        keys_dict['publisher'] = "citation_journal_abbrev"
        keys_dict['pdf_url'] = "citation_pdf_url" 
    
    return keys_dict


def metadata_extracter(path):
    meta_result = dict()
    meta_result['url'] = path 
    
    response = requests.get(path)
    soup = BeautifulSoup(response.text, "html5lib")
    metas = soup.find_all('meta', attrs={'name': True})

    metadata_keys = metadate_keys(path)
    for meta in metas:
        if meta.attrs['name'] == metadata_keys['title']:
            meta_result['title'] = meta.attrs['content']
        elif meta.attrs['name'] == metadata_keys['date']:
            meta_result['date'] = str(meta.attrs['content'].replace('/', '-')).split('-')[0]
        elif meta.attrs['name'] == metadata_keys['publisher']:
            meta_result['publisher'] = meta.attrs['content']
        elif meta.attrs['name'] == metadata_keys['pdf_url']:
            meta_result['pdf_url'] = meta.attrs['content']
    
    return meta_result  

if __name__ == "__main__":
    path = "https://arxiv.org/abs/1809.10341"
    meta = metadata_extracter(path)
    print(meta['title'] + meta['date'])
    # r = requests.get(meta['pdf_url'])
    # with open("test.pdf", "wb+") as f:
    #     f.write(r.content)
    