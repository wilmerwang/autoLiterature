# -*- coding: utf-8 -*- 
import os 
import hashlib
import argparse
import re 
import time 
import operator 

import requests 

from metadata_extract import metadata_extracter
from scihub import SciHub 
import dropbox  


def set_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('--output', type=str, default=None,
                        help='The path to save the pdf format file.')
    parser.add_argument('--dropbox_access_token', type=str, default=None,
                        help='https://www.dropbox.com/developers/documentation/python#tutorial')
    parser.add_argument('--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 


def folder_moniter(moniter_files):
    file_md5 = dict()
    modified_files = []
    
    for md_file in moniter_files:
        if md_file not in file_md5.keys():
            file_md5[md_file] = " "
            
    del_keys =  list(set(file_md5.keys()) - set(moniter_files))
    for key in del_keys:
        del file_md5[key]
    
    for file_path, md5_before in file_md5.items():
        md5_now = hashlib.md5(open(file_path).read().encode('utf-8')).hexdigest()
        if md5_now != md5_before:
            file_md5[file_path] = md5_now
            modified_files.append(file_path)

    return modified_files, file_md5 


def url_download(path, file_path):
    r = requests.get(path)
    with open(file_path, "wb+") as f:
        f.write(r.content)


def sci_hub_download(path, file_path):
    sh = SciHub()
    sh.download(path, file_path) 
    
    
def obtain_dropbox_pdf_url(dbx, file_path):
    dbx_pdf_path = dbx.sharing_create_shared_link(file_path).url
    
    return dbx_pdf_path 


if __name__ == "__main__":
    args = set_args()
    root_path = args.root_path 
    pdf_save_path = args.output 
    interval_time = args.interval_time
    dropbox_access_token = args.dropbox_access_token
    
    # 获得dropbox数据库权限 init 
    dbx = dropbox.Dropbox(dropbox_access_token)
    
    # moniter 
    while True:
        moniter_files = os.listdir(root_path)
        modified_files, file_md5 = folder_moniter(moniter_files)

        pattern = re.compile(r"- \[.*\]\(.*\)")
        for file in modified_files:
            with open(file, 'r') as f:
                lines = f.readlines()
                new_lines = lines.copy()
                for i, line in enumerate(lines[::-1]):
                    m = pattern.match(line)
                    if m:
                        match_str = m.group()
                        citation_path = match_str.split(')')[0].split('(')[-1]
                        
                        # 获得文献的元数据 title,date,...
                        meta_data = metadata_extracter(citation_path)
                        
                        # 下载pdf文献到本地
                        file_name = meta_data['date'] + '_' + meta_data['title'] + '.pdf'
                        file_path = os.path.join(pdf_save_path, file_name)
                        if meta_data['pdf_url']:
                            url_download(meta_data['pdf_url'], file_path)
                        else:
                            sci_hub_download(citation_path, file_path)
                            
                        # 上传本地pdf到dropbox database /pdf 文件夹
                        with open(file_path, 'rb') as f:
                            dbx.files_upload(f.read(), '/pdf/'+file_name, mode=dropbox.files.WriteMode.overwrite)
                        
                        # 获得Dropbox里面pdf链接
                        pdf_url_in_dropbox = obtain_dropbox_pdf_url(dbx, '/pdf/'+file_name)
                        meta_data['pdf_url_in_dropbox'] = pdf_url_in_dropbox 
                        
                        # 要修改的item文件
                        new_line = "- **{}**. **{}**, **{}**, ([pdf]({}))([link]({})) \n".format(meta_data['title'],
                                                                                                meta_data['publisher'], 
                                                                                                meta_data['date'], 
                                                                                                meta_data['pdf_url_in_dropbox'],
                                                                                                citation_path)
                        new_lines[-i-1] = new_line
                    # 
                    # else:
                    #     break 

            # 修改md文件
            if not operator.eq(new_lines, lines):
                with open(file, "w") as f:
                    f.write(''.join(new_lines))
        
        # print("----")
        time.sleep((interval_time))