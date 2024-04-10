import re
from local_data_handler import *

def remove_header(text):
    return re.sub(r'^\d+\n+.+\n+\d+$', '', text, flags=re.MULTILINE)

def prune_text_file(file_path):
    content = get_page_content(file_path)
    # content = content.replace('\ufeff', '')
    content = remove_header(content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    for vol_dir in get_volumes(FIRST_ED):
        for page in get_pages_of_volume(vol_dir):
            prune_text_file(page)

    for vol_dir in get_volumes(FOURTH_ED):
        for page in get_pages_of_volume(vol_dir):
            prune_text_file(page)