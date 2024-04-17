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

def check_subwords(headword, text):
    if len(headword.split(' ')) > 1:
        for word in headword.split(' '):
            word = word.strip(" ,.")
            if len(word) > 1:
                word = re.escape(word)
                pattern = rf"^\d+\s+[^\d\n]*?\b{word}\b[^\d\n]*?\s+\d+$"
                match = re.search(pattern, text, flags=re.MULTILINE)
                if match is not None:
                    return match.group(0)
    return None

def find_header_singleline(text, index):
    first_word = index[0]
    last_word = index[-1]
    if first_word != last_word:
        re_first = re.escape(first_word)
        re_last = re.escape(last_word)
        first_opt = rf"^\d+\s+.*?(?:{re_first})?.*?{re_last}.*?\s+\d+$"
        last_opt = rf"^\d+\s+.*?{re_first}.*?(?:{re_last})?.*?\s+\d+$"
        pattern = first_opt + r"|" + last_opt
        match = re.search(pattern, text, flags=re.MULTILINE)
    else:
        re_word = re.escape(first_word)
        pattern = rf"^\d+\s+.*?{re_word}.*?\s+\d+$"
        match = re.search(pattern, text, flags=re.MULTILINE)
    
    # Some headwords have extra words that are not included in the header
    if match is None:        
        res = check_subwords(first_word, text)
        if res is not None:
            return res
        if first_word != last_word:
            res = check_subwords(last_word, text)
            if res is not None:
                return res
        
    if match is None:
        return None
    return match.group(0)
    

def search_text_file(file_path): # Check results, before removing
    index = get_page_index_only(file_path)
    content = get_page_raw_content(file_path)

    header = find_header_singleline(content, index)

    if header:
        print(f"In {file_path}:")
        print(f"    FOUND: {header}")
        return header

# def remove_header_multiline(text): # Some OCR's wrongly include the page numbers and word-range from the top margin
#     return re.sub(r'^\d+\n+.+\n+\d+$', '', text, count=1, flags=re.MULTILINE)

def prune_text_file(file_path, remove):
    content = get_page_raw_content(file_path)
    content = re.sub(re.escape(remove), "", content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    
def prune_edition_manually(edition):
    seach_results = {}
    for vol_dir in get_volumes(edition):
        for page in get_pages_of_volume(vol_dir):
            found = search_text_file(page)
            if found:
                seach_results[page] = found
        # break
        if seach_results:
            ask_prune = input("Prune? (y/n/cancel): ").lower()
            while ask_prune != 'y' or ask_prune != 'n' or ask_prune != 'cancel':
                if ask_prune == 'y':
                    print(f"PRUNING: {vol_dir}")
                    for file, rm_string in seach_results.items():
                        prune_text_file(file, rm_string)
                    seach_results.clear()
                elif ask_prune == 'n':
                    seach_results.clear()
                    break
                elif ask_prune == 'cancel':
                    print(f"Cancelling...")
                    return
                else:
                    ask_prune = input("Prune? (y/n/cancel): ").lower()

if __name__ == '__main__':
    prune_edition_manually(FIRST_ED)
    # prune_edition_manually(FOURTH_ED)