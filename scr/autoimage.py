# -*- coding: utf-8 -*- 
import os 
import argparse
import re 
import time 

from modules import folderMoniter, patternRecognizer
from modules import dropboxInteractor, note_modified

ROOT = os.path.join(os.path.expanduser('~'), "Dropbox").replace('\\', '/')

def set_args():
    parser = argparse.ArgumentParser(description="AutoImage")
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
    pattern_recog = patternRecognizer(r"\(.*?.png\)")  # 检测 (*.png)
    dbx = dropboxInteractor(dropbox_access_token)

    while True:
        modified_items = folder_moniter.file_md5_update()
        for md_file, md_md5 in modified_items.items():
            with open(md_file, 'r') as f:
                content = f.read()
            
            m = pattern_recog.findall(content)
            if m:
                replace_dict = dict()

                for image in m:
                    image_path = image.split('(')[-1].split(')')[0]
                    print(image_path)

                    # Upload attachment and generate shared link
                    with open(os.path.join(ROOT, image_path), 'rb') as f:
                        dbx.files_upload(f.read(), '/img/'+os.path.split(image_path)[-1])
                    img_shared_link = dbx.generate_shared_url('/img/'+os.path.split(image_path)[-1]).replace('www', 'dl')

                    replace_dict[image] = "(" + img_shared_link + ")"

                # Modified note
                note_modified(pattern_recog, md_file, **replace_dict)

        time.sleep((interval_time))


if __name__ == "__main__":
    main()

