# -*- coding: utf-8 -*- 
import os 
import argparse

import re 
from urllib import parse

from modules import dropboxInteractor

def set_args():
    parser = argparse.ArgumentParser(description="AutoSynchronization")
    parser.add_argument('-p', '--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('-k', '--dropbox_access_token', type=str, default=None,
                        help='https://www.dropbox.com/developers/documentation/python#tutorial')
    args = parser.parse_args()
    
    return args 

def synchronization(root_path, attachment_path, regular_rule, dbx, img=False):

    sharedlinks_files_dict = dbx.sharedlinks_files_list_folder(attachment_path)

    pattern = re.compile(regular_rule)
    md_files = [os.path.join(root_path, p) for p in os.listdir(root_path)]
    sharedlinks_mdfiles = []
    for md_file in md_files:
        with open(md_file, 'r') as f:
            content = f.read()
        m = pattern.findall(content)
        m = [parse.unquote(i) for i in m]

        if img:
            sharedlinks_mdfiles += [i.replace('//dl', '//www') for i in m]
        else:
            sharedlinks_mdfiles += m 

    removed_sharedlinks = list(set(sharedlinks_files_dict.keys()) - set(sharedlinks_mdfiles))
    for sharedlink in removed_sharedlinks:
        dbx.del_file(sharedlinks_files_dict[sharedlink])

    return removed_sharedlinks
        

def main():
    args = set_args()
    root_path = args.root_path
    access_token = args.dropbox_access_token

    dbx = dropboxInteractor(access_token)

    # 
    removed_pdf = synchronization(root_path, '/pdf', r'https://www.dropbox.com/.*?dl=0', dbx)
    print("### Romove pdf: {}".format(removed_pdf))

    removed_img = synchronization(root_path, '/img', r'https://dl.dropbox.com/.*?.png\?dl=0', dbx, img=True)
    print("### Romove images: {}".format(removed_img))

if __name__ == '__main__':
    main()