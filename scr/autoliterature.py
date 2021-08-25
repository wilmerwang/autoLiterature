# -*- coding: utf-8 -*- 
import os 
import argparse
import re 
import time 

from modules import folderMoniter, patternRecognizer, metaExtracter
from modules import urlDownload, dropboxInteractor, note_modified


def set_args():
    parser = argparse.ArgumentParser(description="AutoLiterature")
    parser.add_argument('-p', '--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('-k', '--dropbox_access_token', type=str, default=None,
                        help='https://www.dropbox.com/developers/documentation/python#tutorial')
    parser.add_argument('-t', '--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 


def main():
    args = set_args()
    root_path = args.root_path 
    interval_time = args.interval_time
    dropbox_access_token = args.dropbox_access_token

    # init 
    folder_moniter = folderMoniter(root_path)
    pattern_recog = patternRecognizer(r'- \[.*\]')  # 检测 - [DOI], 或者- [arxivId]
    meta_extracter = metaExtracter()
    url_download = urlDownload()
    dbx = dropboxInteractor(dropbox_access_token)

    while True:
        modified_items = folder_moniter.file_md5_update()
        for md_file, md_md5 in modified_items.items():
            with open(md_file, 'r') as f:
                content = f.read()
            
            m = pattern_recog.findall(content)
            if m:
                replace_dict = dict()

                for literature in m:
                    literature_id = literature.split('[')[-1].split(']')[0]
                    
                    # Fetch data
                    bib_dict = meta_extracter.id2bib(literature_id)
                    pdf_dict = url_download.fetch(literature_id)

                    # Upload attachment and generate shared link
                    if "\n" in bib_dict["title"]:
                        bib_dict["title"] = re.sub(r' *\n *', ' ', bib_dict["title"])
                        
                    pdf_name = bib_dict['year'] + '_' + bib_dict['title'] + '.pdf'
                    if "pdf" in pdf_dict:
                        dbx.files_upload(pdf_dict['pdf'], '/pdf/'+pdf_name)
                        pdf_shared_link = dbx.generate_shared_url('/pdf/'+pdf_name)
                    else:
                        pdf_shared_link = "Please manually add the attachment link."

                    for key in ["title", "author", "journal", "year", "url"]:
                        if key not in bib_dict:
                            bib_dict[key] = "Please manually add this value."

                    replaced_literature = "- **{}**. {} et.al. **{}**, **{}**, ([pdf]({}))([link]({}))".format(
                        bib_dict['title'], bib_dict["author"].split(" and ")[0], bib_dict['journal'], 
                        bib_dict['year'], pdf_shared_link, bib_dict['url']
                        )

                    replace_dict[literature] = replaced_literature

                # Modified note
                note_modified(pattern_recog, md_file, **replace_dict)

        time.sleep((interval_time))


if __name__ == "__main__":
    main()
