import re
from local_data_handler import *

def remove_unrecognized_tags(text): # Prune additional remaining tags that were not detected during scraping
    pattern = r'<\/?([^>bi]+)>' # ex. prunes: span tag from "<b>Abel de Pujol</b> [dö pysjåll], <span class="sp">Alexandre"
                                # found in first/nfaa/0025
    def remove_tags(match):
        tag = match.group(1)
        if tag == 'b' or tag == 'i': # preserve known stylization tags
            return match.group(0)
        return ''
    
    return re.sub(pattern, remove_tags, text)

def find_header_singleline(text, index):
    first_word = re.escape(index[0])
    last_word = re.escape(index[-1])
    if first_word != last_word:
        pattern = rf"^\d+\s+.*?{first_word}.+{last_word}.*?\s+\d+$"
    else:
        pattern = rf"^\d+\s+.*?{first_word}.*?\s+\d+$"
    match = re.findall(pattern, text, flags=re.MULTILINE)
    return match

def search_text_file(file_path): # Check results, before removing
    index = get_page_index_only(file_path)
    content = get_raw_page_content(file_path)

    singleline_header = find_header_singleline(content, index)

    if singleline_header:
        print(f"In {file_path}:")
        print(f"    FOUND: {singleline_header}")

def remove_header_multiline(text): # Some OCR's wrongly include the page numbers and word-range from the top margin
    return re.sub(r'^\d+\n+.+\n+\d+$', '', text, count=1, flags=re.MULTILINE)

def remove_header_singleline(text, index):
    first_word = re.escape(index[0])
    last_word = re.escape(index[-1])
    if first_word != last_word:
        pattern = rf"^\d+\s+.*?{first_word}.+{last_word}.*?\s+\d+$"
    else:
        pattern = rf"^\d+\s+.*?{first_word}.*?\s+\d+$"
    return re.sub(pattern, "", text, count=1, flags=re.MULTILINE)

def prune_text_file(file_path):
    index = get_page_index_only(file_path)
    content = get_raw_page_content(file_path)
    # content = content.replace('\ufeff', '')
    # content = remove_header_multiline(content)
    # content = remove_unrecognized_tags(content)
    content = remove_header_singleline(content, index)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    for vol_dir in get_volumes(FIRST_ED):
        for page in get_pages_of_volume(vol_dir):
            # search_text_file(page)
            prune_text_file(page)

    for vol_dir in get_volumes(FOURTH_ED):
        for page in get_pages_of_volume(vol_dir):
            # search_text_file(page)
            prune_text_file(page)