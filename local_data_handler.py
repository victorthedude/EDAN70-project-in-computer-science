import os
FIRST_ED = f"data\\nf_first_edition"
FOURTH_ED = f"data\\nf_fourth_edition"

def get_volumes(edition_path):
    vol_dirs = [f.path for f in os.scandir(edition_path) if f.is_dir()]
    return vol_dirs

def get_pages_of_volume(volume_path):
    pages = [f.path for f in os.scandir(volume_path) if f.is_file()]
    return pages

def get_page_content(page_path):
    with open(page_path, 'r', encoding='utf-8-sig') as f: # utf-8-sig automatically handles any UTF-8 BOM's at the beginning of files
        content = f.read()
    return content