from local_data_handler import *
import re
from Levenshtein import ratio as levenshtein_ratio
import json

def get_headword_from_bold(string):
    # Check if string contains <b> tag
    match = re.search(r'<b>(.+)<\/b>', string)
    if match is None:
        return None
    return match.group(1).strip(' ,.')

def check_italics_tag(string):
    return

def get_headword_from_index(text: str, index: list[str]):
    text = remove_tags(text)
    for headword in index:
        headword_count = len(headword.split(' '))
        headword = headword.strip(' ,.')
        first_words = [word.strip(' ,.') for word in re.sub("\s+"," ",text).split(' ')[:2+headword_count]]
        if headword_count > 1: # If headword consists of more than one word:
            for i in range(0,len(first_words)-headword_count):
                # if i+headword_count > len(headword_count):
                #     break
                comp_word = " ".join(first_words[i:i+headword_count])
                if headword == comp_word:
                    return headword
        else:
            if headword in first_words:
              return headword
    return None

def get_headword_by_score(text, index):
    # "normalize" text by removing spaces and punctuation:
    text = re.sub(r"[.,'\s]", "", remove_tags(text))

    scores = [0 for _ in range(len(index))]
    headword_candidates = []
    for i, headword in enumerate(index):
        # "normalize" headword:
        headword_norm = re.sub(r"[.,'\s]", "", headword)
        sim_score = levenshtein_ratio(headword_norm, text[:len(headword_norm)]) 
        if sim_score >= (len(headword_norm)-1) / len(headword_norm): # one char error/edit ratio
            # print(f"Found '{headword}' for '{text}' with {sim_score}")
            headword_candidates.append(headword)
        else:
            scores[i] = sim_score
    if headword_candidates:
        # heuristic: if we find multiple headword candidates, choose the longest headword.
        best = max(headword_candidates, key=len)
        # print(f"  Chose '{best}' for '{text}'")
        return best

    headword = None
    best_score = 0
    # If nothing else; go for highest reasonable (>=0.6) similarity score:
    for i in range(len(scores)):
        score = scores[i]
        if score >= 0.6 and score > best_score: # '0.6' is usually considered "close enough"
            best_score = score
            headword = index[i]
            # print(f"Found '{headword}' for '{text}' with {best_score}")

    return headword

def remove_tags(string):
    return re.sub(r'<\/?[^>]+>|\[[^\]]+\]', '', string) # removes ALL tags + phonetics fluff?.

def extract_headword(text, index):
    first_line = re.search(r'^(.+)\n?', text).group(1)

    # To assign a certain paragraph/text to an entry:
    # 1. First check for bold tag:
    headword = get_headword_from_bold(first_line)
    if headword:
        return headword
    # 2. Then check index:
    headword = get_headword_from_index(first_line, index)
    if headword:
        return headword
    # 3. Then use string similarity scoring:
    headword = get_headword_by_score(first_line, index)
    if headword:
        return headword

    # OBS: prune tags from text when doing similarity scoring
    return headword

def extract_entries_from_page(page_path, current_entry_nbr, volume_nbr, edition):
    index, content = get_page_index_and_content(page_path)
    entries = []
    paragraphs = [paragraph.strip('\n') for paragraph in content.split('\n\n')]
    # print(f"INDEX: {index}")
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
        
        # Check if there is more than one period, if so: remove fluff after the last period
        if text.count('.') > 1:
            text = re.sub(r'\.[^.]+$', '', text) # remove everything after the last period ?

        headword = extract_headword(text, index)
        if headword is None: # if no headword could be found, skip paragraph (?)
            continue
        entry["headword"] = headword
        entry["entryId"] = f"e{edition}_v{volume_nbr}_{current_entry_nbr}"
        entry["text"] = text.replace('\n', ' ') # replace newlines with space
        entries.append(entry)
        current_entry_nbr += 1

        text = text.replace('\n', ' ')

    return entries, current_entry_nbr

if __name__ == '__main__':
    test_1 = 'data\\nf_first_edition\\nfaf\\0745.txt'  # missing index, but has bold tags
    test_2 = 'data\\nf_fourth_edition\\nffp\\0015.txt' # complete index but different spelling/format of headwords in index and in text, no bold tags
    test_3 = 'data\\nf_first_edition\\nfaa\\0024.txt'  # straight-forward; complete index + bold tags
    test_4 = 'data\\nf_first_edition\\nfaa\\1299.txt'  # complete index but has a bunch of character errors in text. no bold-tags.

    test = f'{FIRST_ED}\\nfaa\\1525.txt' # Bank
    # test = f'{FOURTH_ED}\\nffa\\0165.txt'
    # test = f'{FIRST_ED}\\nffr\\0019.txt' # Richert family

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