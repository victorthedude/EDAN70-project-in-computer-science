import os
import json
FIRST_ED_TEXT = "data\\nf_first_edition"
FOURTH_ED_TEXT = "data\\nf_fourth_edition"
FIRST_ED_JSON = "data\\json\\first_ed"
FOURTH_ED_JSON = "data\\json\\fourth_ed"

def get_volumes(edition_path):
    vol_dirs = [f.path for f in os.scandir(edition_path) if f.is_dir()]
    return vol_dirs

def get_pages_of_volume(volume_path):
    pages = [f.path for f in os.scandir(volume_path) if f.path.endswith('.txt')]
    return pages

def get_page_raw_content(page_path):
    with open(page_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig automatically handles any UTF-8 BOM's at the beginning of files
        content = f.read()
    return content

def get_page_index_only(page_path) -> list[str]:
    index = []
    with open(page_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig automatically handles any UTF-8 BOM's at the beginning of files
        line = f.readline()
        while line.startswith('- '):
            entry = line.strip('\n- ')
            index.append(entry)
            line = f.readline()
    return index

def get_page_content_only(page_path):
    with open(page_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig automatically handles any UTF-8 BOM's at the beginning of files
        line = f.readline()
        while line.startswith('- '):
            line = f.readline()
        content = f.read()
    return content

def get_page_index_and_content(page_path):
    index = []
    with open(page_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig automatically handles any UTF-8 BOM's at the beginning of files
        line = f.readline()
        while line.startswith('- '):
            entry = line.strip('\n- ')
            index.append(entry)
            line = f.readline()
        content = f.read()
    return index, content

def get_jsons_of_dir(dir_path):
    jsons = [f.path for f in os.scandir(dir_path) if f.path.endswith('.json')]
    return jsons

def load_json(json_path):
    with open(json_path, 'r', encoding='utf-8-sig') as f:
        content = json.load(f)
    return content