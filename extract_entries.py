from local_data_handler import *
import re
from difflib import SequenceMatcher
import json

def similar(a, b): # string similarity scoring
        return SequenceMatcher(None, a, b).ratio()

def get_headword_from_bold(string):
    # Check if string contains <b> tag
    match = re.search(r'<b>(.+)<\/b>', string)
    if match is None:
        return None
    return match.group(1).strip(' ,')

def check_italics_tag(string):
    return

def get_headword_from_index(text, index):
    # text = remove_tags(text)
    scores = [0 for i in range(len(index))]
    for i, headword in enumerate(index):
        # if text.startswith(headword):
        if headword in text:
            return headword, scores
        sim_score = similar(headword, remove_tags(text)[:len(headword)]) # very small character differences can still remain
        if sim_score > 0.9:                                              # after regex substituion. check similarity and assign  
            return headword, scores                                      # directly if VERY similar.
        else:
            scores[i] = sim_score

    return None, scores

def remove_tags(string):
    return re.sub(r'<\/?[^>]+>|\[[^\]]+\]', '', string) # removes ALL tags + phonetics fluff?.

def extract_headword(text, index):
    first_line = re.search(r'^(.+)\n?', text).group(1)

    # To assign a certain paragraph/text to an entry:
    # 1. First check index:
    headword, sim_scores = get_headword_from_index(first_line, index)
    if headword:
        return headword
    # 2. Then check for bold tag:
    headword = get_headword_from_bold(first_line)
    if headword:
        return headword
    # 3. If nothing else; go for highest reasonable (>0.8) similarity score:
    best_score = 0
    for i in range(len(sim_scores)):
        score = sim_scores[i]
        if score > 0.8 and score > best_score:
            best_score = score
            headword = index[i]
    # OBS: prune tags from text when doing similarity scoring
    return headword

def extract_entries_from_page(page_path, current_entry_nbr, volume_nbr, edition):
    index, content = get_page_index_and_content(page_path)
    entries = []
    paragraphs = [paragraph.strip('\n') for paragraph in content.split('\n\n')]
    for paragraph in paragraphs:
        if not paragraph: # some documents can include more newlines than usual which results in "empty" paragarphs
            continue
        entry = {
            "headword":"",
            "entryId": current_entry_nbr, # entryId = volnbr_entrynbr_revision
            "text":"",
            "person":0,
            "qid":"",
        }
        text = paragraph[:208] # limit to 200 + 8 characters per entry, 
        # 200 chars approx. equals 4-5 lines in a paragraph => 4-5 \n chars => +8 characters to account for newline chars.
        text = re.sub(r'\.[^.]+$', '', text) # remove everything after the last period ?

        first_line = re.search(r'^(.+)\n?', text).group(1)
        headword = extract_headword(first_line, index)
        if headword is None: # if no headword could be found, skip paragraph
            continue
        entry["headword"] = headword
        entry["entryId"] = f"e{edition}_v{volume_nbr}_{current_entry_nbr}"
        entry["text"] = text.replace('\n', ' ') # replace newlines with space
        entries.append(entry)
        current_entry_nbr += 1

    return entries, current_entry_nbr

if __name__ == '__main__':
    test_1 = 'data\\nf_first_edition\\nfaf\\0745.txt'  # missing index, but has bold tags
    test_2 = 'data\\nf_fourth_edition\\nffp\\0015.txt' # complete index but different spelling/format of headwords in index and in text, no bold tags
    test_3 = 'data\\nf_first_edition\\nfaa\\0024.txt'  # straight-forward; complete index + bold tags
    test_4 = 'data\\nf_first_edition\\nfaa\\1299.txt'  # complete index but has a bunch of character errors in text. no bold-tags.

    test = f'{FIRST_ED}\\nfaa\\1525.txt'

    entries, _ = extract_entries_from_page(test, 1, 1, 1)
    with open("sample.json", "w", encoding='utf-8') as outfile: 
        json.dump(entries, outfile, ensure_ascii=False)
    
    # all_entries_of_vol = []
    # entry_nbr = 1
    # i = 0
    # for vol_nbr, volume_path in enumerate(get_volumes(FIRST_ED), start=1):
    #     if i == 1:
    #         break
    #     for page_path in get_pages_of_volume(volume_path):
            
    #         entries, entry_nbr = extract_entries_from_page(page_path, entry_nbr, vol_nbr, 1)
    #         all_entries_of_vol += entries

    #     volume = volume_path.split('\\')[-1]
    #     with open(f"data/json/first_ed/{volume}.json", "w", encoding='utf-8') as outfile: 
    #         json.dump(all_entries_of_vol, outfile, ensure_ascii=False)
    #     i += 1
    #     all_entries_of_vol.clear()