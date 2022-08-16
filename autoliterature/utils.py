import os 
import hashlib
import re 

class folderMoniter(object):
    def __init__(self, folder_path):
        self.folder_path = folder_path

        self.file_md5 = dict()

    def _files_in_folder(self):
        return [os.path.join(self.folder_path, p) for p in os.listdir(self.folder_path)]

    def file_md5_update(self):
        files = self._files_in_folder()

        added_files = list(set(files) - set(self.file_md5.keys()))
        self.file_md5.update(zip(added_files, [' ']*len(added_files)))

        removed_files = list(set(self.file_md5.keys()) - set(files))
        for removed_file in removed_files:
            del self.file_md5[removed_file]

        modified_items = dict()
        for file_path, md5_before in self.file_md5.items():
            md5_now = hashlib.md5(open(file_path).read().encode('utf-8')).hexdigest()
            if md5_now != md5_before:
                self.file_md5[file_path] = md5_now
                modified_items[file_path] = md5_now

        return modified_items 
    
    

class patternRecognizer(object):
    def __init__(self, regular_rule):
        self.pattern = re.compile(regular_rule)

    def match(self, string):
        return self.pattern.match(string)
    
    def findall(self, string):
        return self.pattern.findall(string)

    def multiple_replace(self, content, **replace_dict):
        def replace_(value):
            match = value.group()
            if match in replace_dict.keys():
                return replace_dict[match]
            else:
                return match+" **Not Correct, Check it**"
        
        replace_content = self.pattern.sub(replace_, content)
        
        return replace_content
    

def note_modified(pattern_recog, md_file, **replace_dict):
    with open(md_file, 'r') as f:
        content = f.read()
    
    replaced_content = pattern_recog.multiple_replace(content, **replace_dict)

    with open(md_file, 'w') as f:
        f.write(''.join(replaced_content))
        
 
def get_pdf_paths(pdf_root):
    pdf_paths = []
    for root, _, files in os.walk(pdf_root):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))
                
    return pdf_paths
 
        
def get_pdf_paths_from_notes(md_root, reg):
    
    md_files = []
    for root, _, files in os.walk(md_root):
        for file in files:
            if file.lower().endswith('md') or file.lower().endswith('markdown'):
                md_files.append(os.path.join(root, file))
    
    pdf_paths_from_notes = []
    for md_file in md_files:
        with open(md_file, 'r') as f:
            content = f.read()
        m = reg.findall(content)
        m = [i.split("(")[-1].split(')')[0] for i in m]
        pdf_paths_from_notes.extend(m)

    return pdf_paths_from_notes