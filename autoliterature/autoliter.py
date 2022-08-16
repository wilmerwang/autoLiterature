import logging 
import argparse
import os 
import configparser
from turtle import st
from tqdm import tqdm 

from utils import patternRecognizer, note_modified, get_pdf_paths, get_pdf_paths_from_notes
from downloads import get_paper_info_from_paperid, get_paper_pdf_from_paperid


logging.basicConfig()
logger = logging.getLogger('AutoLiter')
logger.setLevel(logging.INFO)


def set_args():
    parser = argparse.ArgumentParser(description='autoLiterature')
    parser.add_argument('-i', '--input', required=True, type=str, default=None,
                        help="The path to the note file or note file folder.")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Folder path to save paper pdfs and iamges. NOTE: MUST BE FOLDER')
    parser.add_argument('-p', '--proxy', type=str, default="127.0.0.1:7890", 
                        help='The proxy. e.g. 127.0.0.1:1080')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Delete unreferenced attachments in notes. Use with caution, '
                        'when used, -i must be a folder path including all notes')
    parser.add_argument('-m', '--migration', type=str, default=None, 
                        help="the pdf folder path you want to reconnect to")
    args = parser.parse_args()
    
    return args 

def check_args():
    args = set_args()
    input_path = args.input
    output_path = args.output 
    delete_bool = args.delete
    migration_path = args.migration
    proxy = args.proxy
        
    return input_path, output_path, delete_bool, proxy, migration_path


def get_bib_and_pdf(note_file, output_path, proxy, paper_recognizer, pdf=False):
    
    pdfs_path = os.path.join(output_path, "pdfs")
    if not os.path.exists(pdfs_path):
        os.makedirs(pdfs_path)
    
    with open(note_file, 'r') as f:
            content = f.read()
            
    m = paper_recognizer.findall(content)
    if pdf:
        logger.info("需要下载的文献(With PDF) 个数 - {}".format(len(m)))
        logger.info(m)
    else:
        logger.info("需要下载的文献(Without PDF) 个数 -  {}".format(len(m)))
        logger.info(m)

    if not m:
        logger.info("文件 {} 未更新.".format(note_file))
    else:
        replace_dict = dict()
        
        for literature in tqdm(m):
            literature_id = literature.split('{')[-1].split('}')[0]
            bib = get_paper_info_from_paperid(literature_id, proxy=proxy)
            try:
                pdf_name = '_'.join(bib['title'].split(' ')) + '.pdf'
                pdf_path = os.path.join(pdfs_path, pdf_name)
                
                if pdf:
                    if not os.path.exists(pdf_path):
                        get_paper_pdf_from_paperid(literature_id, pdf_path, direct_url=bib['pdf_link'], proxy=proxy)
                        if not os.path.exists(pdf_path):
                            get_paper_pdf_from_paperid(literature_id, pdf_path, proxy=proxy)

                if os.path.exists(pdf_path):
                    replaced_literature = "- **{}**. {} et.al. **{}**, **{}**, ([pdf]({}))([link]({})).".format(
                                        bib['title'], bib["author"].split(" and ")[0], bib['journal'], 
                                        bib['year'], os.path.relpath(pdf_path, note_file).split('/',1)[-1], 
                                        bib['url'])
                    print(pdf_path, note_file)
                else:
                    replaced_literature = "- **{}**. {} et.al. **{}**, **{}**, ([link]({})).".format(
                                        bib['title'], bib["author"].split(" and ")[0], bib['journal'], 
                                        bib['year'], bib['url']
                                        )
                replace_dict[literature] = replaced_literature
            except:
                logger.info("文献下载失败，已经跳过 {}".format(literature_id))
            
        return replace_dict


def file_update(input_path, output_path, proxy, paper_recognizer_with_pdf, 
                paper_recognizer_without_pdf):
    
    replace_dict_with_pdf =  get_bib_and_pdf(input_path, output_path,
                                             proxy, paper_recognizer_with_pdf,
                                             pdf=True)
    replace_dict_without_pdf = get_bib_and_pdf(input_path, output_path,
                                               proxy, paper_recognizer_without_pdf)
    
    if replace_dict_with_pdf:
        note_modified(paper_recognizer_with_pdf, input_path, **replace_dict_with_pdf)
    if replace_dict_without_pdf:
        note_modified(paper_recognizer_without_pdf, input_path, **replace_dict_without_pdf)


def main():
    input_path, output_path, delete_bool, proxy, migration_path = check_args()
    
    if output_path:
        paper_recognizer_with_pdf = patternRecognizer(r'- \{\{.{3,}\}\}')  # - {{doi}}
        paper_recognizer_without_pdf = patternRecognizer(r'- \{(?!\{).{3,}\}')   # - {doi}  (?!\{)
        
        if os.path.isfile(input_path):
            logger.info("正在更新文件 {}".format(input_path))
            file_update(input_path, output_path, proxy, paper_recognizer_with_pdf, 
                    paper_recognizer_without_pdf)
            
        elif os.path.isdir(input_path):
            note_paths = []
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith('md') or file.lower().endswith('markdown'):
                        note_paths.append(os.path.join(root, file))
            for note_path in note_paths:
                logger.info("正在更新文件 {}".format(note_path))
                file_update(note_path, output_path, proxy, paper_recognizer_with_pdf, 
                    paper_recognizer_without_pdf)
        else:
            logger.info("input path {} is not exists".format(input_path))
    
    
    # Delete unreferenced attachments
    if delete_bool:
        if os.path.isfile(input_path):
            logger.info("输入的路径必须是笔记总文件夹!!!请谨慎使用该参数!!!")
        else:
            pdf_path_recognizer = patternRecognizer(r'\[pdf\]\(.{5,}\.pdf\)')
            pdf_paths_in_notes = get_pdf_paths_from_notes(input_path, pdf_path_recognizer)
            pdf_paths = get_pdf_paths(output_path)
            # TODO mac 和 win 之间路径可能会不同，“/” 和 “\\”
            pdf_paths_in_notes = [os.path.abspath(i) for i in pdf_paths_in_notes]
            pdf_paths = [os.path.abspath(i) for i in pdf_paths]
            
            removed_pdf_paths = list(set(pdf_paths - set(pdf_paths_in_notes)))
            try:
                for pdf_p in removed_pdf_paths:
                    os.remove(pdf_p)
            except:
                pass 
            
            logger.info("已删除 {} 个PDF文件".format(len(removed_pdf_paths)))
            
    
    if migration_path:
        logger.info("迁移功能还未添加,会尽快添加.")
    
    if not output_path and  not delete_bool and not migration_path:
        logger.info("缺少关键参数 -o 或者 -d 或者 -m, 程序未运行, 请使用 -h 查看具体信息")


if __name__ == "__main__":
    main()