import re
from local_data_handler import *

def remove_header(text): # Some OCR's wrongly include the page numbers and word-range at the top
    return re.sub(r'^\d+\n+.+\n+\d+$', '', text, flags=re.MULTILINE)

def remove_unrecognized_tags(text): # Prune additional remaining tags that were not detected during scraping
    pattern = r'<\/?([^>bi]+)>' # ex. prunes: span tag from "<b>Abel de Pujol</b> [dö pysjåll], <span class="sp">Alexandre"
                                # found in first/nfaa/0025
    def remove_tags(match):
        tag = match.group(1)
        if tag == 'b' or tag == 'i': # preserve known stylization tags
            return match.group(0)
        return ''
    
    return re.sub(pattern, remove_tags, text)

def prune_text_file(file_path):
    content = get_raw_page_content(file_path)
    # content = content.replace('\ufeff', '')
    # content = remove_header(content)
    content = remove_unrecognized_tags(content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    for vol_dir in get_volumes(FIRST_ED):
        for page in get_pages_of_volume(vol_dir):
            prune_text_file(page)

    for vol_dir in get_volumes(FOURTH_ED):
        for page in get_pages_of_volume(vol_dir):
            prune_text_file(page)