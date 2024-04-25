import regex as re
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
                pattern = rf"^\d+\s+[^\d\s]*?\b{word}\b[^\d\s]*?\s+\d+$"
                match = re.search(pattern, text, flags=re.MULTILINE)
                if match is not None:
                    return match.group(0)
    return None

def find_header_singleline(text, index, first_index=0, last_index=-1):
    first_word = index[first_index]
    last_word = index[last_index]
    if first_word != last_word:
        re_first = re.escape(first_word)
        re_last = re.escape(last_word)
        first_opt = rf"^\d+\s+.*?(?:\b{re_first}\b)?.*?\b{re_last}\b.*?\s+\d+$"
        last_opt = rf"^\d+\s+.*?\b{re_first}\b.*?(?:\b{re_last}\b)?.*?\s+\d+$"
        pattern = first_opt + r"|" + last_opt
        match = re.search(pattern, text, flags=re.MULTILINE)
    else:
        re_word = re.escape(first_word)
        pattern = rf"^\d+\s+.*?\b{re_word}\b.*?\s+\d+$"
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
    # content = get_page_raw_content(file_path)

    # header = find_header_singleline(content, index)
    # if len(index) > 1 and not header:
    #     # headwords can stretch to an additional page and be included first in the index
    #     # while the header however will not include it in the page title
    #     header = find_header_singleline(content, index, 1, -2)

    header = find_members_of_family(index)
    # header = re.findall(r'[^\n]+\n[ \t]*(\p{L}\. \p{L}\.)[ \t]*\n[^\n]+', content, flags=re.MULTILINE)

    if header:
        print(f"In {file_path}:")
        print(f"    FOUND: {header}")
        return header

# def remove_header_multiline(text): # Some OCR's wrongly include the page numbers and word-range from the top margin
#     return re.sub(r'^\d+\n+.+\n+\d+$', '', text, count=1, flags=re.MULTILINE)

NAME = r"(?:\(?\p{Lu}\p{Ll}*\)?[ \t]?)"
PARTICLE = r"(?:\(?\p{Lu}?\p{Ll}*\)?[ \t]?)"
FIRST_ED_PATTERN = rf"^\d+\.[ \t]{NAME}{PARTICLE}*,[ \t]{NAME}{PARTICLE}*$"
FOURTH_ED_PATTERN = rf"{NAME}{PARTICLE}*,[ \t]\d+\.[ \t]{NAME}{PARTICLE}*"
FAMILY_MEMBER_PATTERN = re.compile(FIRST_ED_PATTERN + r"|" + FOURTH_ED_PATTERN)
def find_members_of_family(index):
    matches = []
    for headword in index:
        match = re.search(FAMILY_MEMBER_PATTERN, headword)
        if match:
            matches.append(match.group(0))
    # if matches:
    #     print(matches)
    return matches

def prune_text_file(file_path, remove):
    content = get_page_raw_content(file_path)
    content = re.sub(re.escape(remove), "", content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    
def prune_edition_manually(edition):
    seach_results = {}
    for vol_dir in get_volumes(edition):
        for page in get_pages_of_volume(vol_dir):
            # print(f"SEARCHING IN: {page}")
            found = search_text_file(page)
            # if found:
            #     seach_results[page] = found
        # break
        # ask_prune = input("Prune? (y/n/cancel): ").lower()
        # if seach_results:
        #     ask_prune = input("Prune? (y/n/cancel): ").lower()
        #     while ask_prune != 'y' or ask_prune != 'n' or ask_prune != 'cancel':
        #         if ask_prune == 'y':
        #             # for file, rm_string in seach_results.items():
        #             #     print(f"PRUNING: '{rm_string}' from {file}...")
        #             #     prune_text_file(file, rm_string)
        #             seach_results.clear()
        #             break
        #         elif ask_prune == 'n':
        #             seach_results.clear()
        #             break
        #         elif ask_prune == 'cancel':
        #             print(f"Cancelling...")
        #             return
        #         else:
        #             ask_prune = input("Prune? (y/n/cancel): ").lower()

if __name__ == '__main__':
    prune_edition_manually(FIRST_ED_TEXT)
    # prune_edition_manually(FOURTH_ED)