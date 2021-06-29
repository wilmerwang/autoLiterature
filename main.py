# -*- coding: utf-8 -*- 
import os 
import argparse 

from concurrent.futures import ThreadPoolExecutor as Executor 

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

def set_args():
    parser = argparse.ArgumentParser(description='autoLiterature')
    parser.add_argument('-p', '--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('-k', '--dropbox_access_token', type=str, default=None,
                        help='https://www.dropbox.com/developers/documentation/python#tutorial')
    parser.add_argument('-t', '--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 

def autoliter(root_path, dropbox_access_token, interval_time):
    os.system("python {}/scr/autoliterature.py -p {} -k {} -t {}".format(FILE_PATH,
                                                                         root_path,
                                                                         dropbox_access_token,
                                                                         interval_time))

def autoimg(root_path, dropbox_access_token, interval_time):
    os.system("python {}/scr/autoimage.py -p {} -k {} -t {}".format(FILE_PATH,
                                                                    root_path,
                                                                    dropbox_access_token,
                                                                    interval_time))


def main():
    args = set_args()
    root_path = args.root_path
    dropbox_access_token = args.dropbox_access_token
    interval_time = args.interval_time
    
    with Executor(max_workers=2) as executor: 
        task1 = executor.submit(autoliter, root_path, dropbox_access_token, interval_time)
        task2 = executor.submit(autoimg,root_path, dropbox_access_token, interval_time)

if __name__ == "__main__":
    main()