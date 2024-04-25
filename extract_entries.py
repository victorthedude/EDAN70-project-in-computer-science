from local_data_handler import *
import regex as re
from Levenshtein import ratio as levenshtein_ratio
import json
import sys

def get_headword_from_bold(string):
    # Check if string contains <b> tag
    match = re.search(r'<b>(.+)<\/b>', string)
    if match is None:
        return None
    # print(f"(BOLD) Found '{match.group(1).strip(' ,.')}' from '{string}'")
    return match.group(1).strip(' ,.')

def check_italics_tag(string):
    return

def split_even(text) -> list[str]:
    res = re.sub("\s+", " ", text)
    res = list(filter(bool, [word.strip(' ,.') for word in res.split(' ')]))
    return res

HEADWORD_OFFSET = 1
def get_headword_from_index(text: str, index: list[str]):
    text = remove_tags(text)
    candidates = []
    words = split_even(text)
    for headword in index:
        headword_count = len(headword.split(' '))
        headword = headword.strip(' ,.')
        first_words = words[:HEADWORD_OFFSET+headword_count]
        if headword_count > 1: # If headword consists of more than one word:
            for i in range(0,len(first_words)-headword_count):
                comp_words = first_words[i:i+headword_count]
                if split_even(headword) == comp_words:
                    # print(f"(INDEX) Found '{headword}' in {first_words}")
                    candidates.append(headword)
        else:
            if headword in first_words:
                # print(f"(INDEX) Found '{headword}' in {first_words}")
                candidates.append(headword)
    if candidates:
        longest = max(candidates, key=len)
        # print(f"(INDEX)     Chose '{longest}' for {text}")
        return longest

    return None

def normalize_text(text):
    return re.sub(r"[.,' \t]", "", text)

MIN_SCORE_THRESHOLD = 0.7
def get_headword_by_score(text, index):
    # "normalize" text by removing spaces and punctuation:
    text = normalize_text(remove_tags(text))

    scores = [0 for _ in range(len(index))]
    candidates = []
    for i, headword in enumerate(index):
        # "normalize" headword for comparison:
        headword_norm = normalize_text(headword)
        sim_score = levenshtein_ratio(headword_norm, text[:len(headword_norm)]) 
        if len(headword) > 1 and sim_score >= (len(headword_norm)-1) / len(headword_norm): # one char error/edit ratio
            # print(f"(SCORE) Found '{headword}' for '{text}' with {sim_score}")
            candidates.append(headword)
        else:
            scores[i] = sim_score
    if candidates:
        # heuristic: if we find multiple headword candidates, choose the longest headword.
        longest = max(candidates, key=len)
        # print(f"(SCORE)   Chose '{longest}' for '{text}'")
        return longest

    headword = None
    best_score = 0
    # If nothing else; go for highest reasonable similarity score:
    for i in range(len(scores)):
        score = scores[i]
        if score >= MIN_SCORE_THRESHOLD and score > best_score: # '0.6' is usually considered "close enough"
            best_score = score
            headword = index[i]
            # print(f"(SCORE) Found '{headword}' for '{text}' with {best_score}")

    # if headword is not None:
        # print(f"(SCORE)   Chose '{headword}' for '{text}'")

    return headword

def remove_tags(string): # remove parenthesis+content within parenthesis as well?
    return re.sub(r'<\/?[^>]+>|\[[^\]]+\]', '', string) # removes ALL tags + phonetics fluff?.

def extract_headword(text, index):
    first_line = re.search(r'^(.+)\n?', text).group(1)

    # To assign a certain paragraph/text to an entry:
    # 1. First check for bold tag:
    headword = get_headword_from_bold(first_line)
    if headword:
        return headword
    # 2. Then check using index:
    headword = get_headword_from_index(first_line, index)
    if headword:
        return headword
    # 3. Then use string similarity scoring:
    headword = get_headword_by_score(first_line, index)
    if headword:
        return headword

    return headword


MIN_MEMBER_SCORE_THRESHOLD = 0.7
def extract_family_member(text, family_members):
    first_line = re.search(r'^(.+)\n?', text).group(1)
    first_line_norm = normalize_text(first_line).lower()
    
    first_ed_index_pat = r"(\d+)\.[ \t].+,(.+)"
    fourth_ed_index_pat = r".+,[ \t](\d+)\.[ \t](.+)"
    # index_pat = re.compile(first_ed_index_pat + r"|" + fourth_ed_index_pat)
    first_ed_text_pat = r"\d+\.[ \t].+,(.+)"
    fourth_ed_text_pat = r"\d+\)(.+)"
    # text_pat = re.compile(first_ed_text_pat + r"|" + fourth_ed_text_pat)

    candidates = []
    for member in family_members:
        index_member_match = re.search(first_ed_index_pat, member)
        if index_member_match is None:
            index_member_match = re.search(fourth_ed_index_pat, member)
        digit = index_member_match.group(1)
        first_name = index_member_match.group(2)
        if digit in first_line_norm[:len(first_name)]:
            first_name_norm = re.sub(r"[ \t]", "", first_name).lower()
            if first_name_norm in first_line_norm:
                # print(f"(MEMBER)   Chose '{member}' for '{first_line}'")
                return member
            else:
                line_match = re.search(first_ed_text_pat, first_line_norm)
                if line_match is None:
                    line_match = re.search(fourth_ed_text_pat, first_line_norm)
                if line_match is None: # safety net; in case a non-person paragraph makes it this far
                    break

                name_in_text = line_match.group(1)
                score = levenshtein_ratio(first_name_norm, name_in_text[:len(first_name_norm)])
                if score >= MIN_MEMBER_SCORE_THRESHOLD:
                    # print(f"(MEMBER) Found '{member}' for '{first_line}' with {score}")
                    candidates.append( (member, score) )

    if candidates:
        member, score = max(candidates, key=lambda x: x[1])
        # print(f"(MEMBER)   Chose '{member}' for '{first_line}' with {score}")
        return member
    
    return None


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

def extract_entries_from_page(page_path, current_entry_nbr, volume_nbr, edition):
    index, content = get_page_index_and_content(page_path)
    paragraphs = [paragraph.strip('\n') for paragraph in content.split('\n\n') if paragraph]
    members_of_family = find_members_of_family(index)
    # print(f"Extracting entries from: {page_path}")
    # print(f"INDEX: {index}")
    # print(f"MEMBERS: {members_of_family}")

    # missed = []
    entries = []
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
        if headword is None:
            if members_of_family:
                headword = extract_family_member(text, members_of_family)

        if headword is None: # if no headword could be found, skip paragraph (?)
            # missed.append(paragraph[:50])
            continue


        entry["headword"] = headword
        entry["entryId"] = f"e{edition}_v{volume_nbr}_{current_entry_nbr}"
        entry["text"] = text.replace('\n', ' ') # replace newlines with space
        entries.append(entry)
        current_entry_nbr += 1

        text = text.replace('\n', ' ')

    # if missed:
    #     print(f"({page_path})")
    #     print(f"INDEX:  {index}")
    #     print(f"MISSED:\n{missed}")

    return entries, current_entry_nbr

if __name__ == '__main__':
    # test = 'data\\nf_first_edition\\nfaf\\0745.txt'  # missing index, but has bold tags
    # test = 'data\\nf_fourth_edition\\nffp\\0015.txt' # complete index but different spelling/format of headwords in index and in text, no bold tags
    # test = 'data\\nf_first_edition\\nfaa\\0024.txt'  # straight-forward; complete index + bold tags
    # test = 'data\\nf_first_edition\\nfaa\\1299.txt'  # complete index but has a bunch of character errors in text. no bold-tags.

    # test = f'{FIRST_ED}\\nfaa\\0693.txt' # Anckarsvärd family (1st ed), no paragraph separation
    # test = f'{FIRST_ED}\\nfaa\\0697.txt' # Anckarsvärd family (1st ed)
    # test = f'{FIRST_ED}\\nfaj\\0017.txt' # Lode family (1st ed)

    # test = f'{FOURTH_ED}\\nffr\\0019.txt' # Richert family
    # test = f'{FOURTH_ED}\\nffa\\0059.txt' # Adelswärd family
    # test = f'{FOURTH_ED}\\nffi\\0512.txt' # Hammarskjöld
    # test = f'{FOURTH_ED}\\nffa\\0586.txt' # Astor
    # test = f'{FOURTH_ED}\\nffc\\0582.txt' # Brun
    # test = f'{FOURTH_ED}\\nffc\\0430.txt' # Brahe

    # test = "data\\nf_first_edition\\nfac\\0327.txt"

    # https://runeberg.org/nffp/0454.html # "Paget Violet"
    # test = "data\\nf_fourth_edition\\nffp\\0454.txt"
    # https://runeberg.org/nffs/0235.html # "SKODA JOSEPH"
    # test = "data\\nf_fourth_edition\\nffs\\0235.txt"
    # https://runeberg.org/nffs/0041.html # "Service, Robert"
    # test = "data\\nf_fourth_edition\\nffs\\0041.txt"

    # test = "data\\nf_first_edition\\nfat\\1150.txt"

    # print(f"Extracting entries from: {test}")
    # entries, _ = extract_entries_from_page(test, 1, 1, 1)
    # with open("sample.json", "w", encoding='utf-8') as outfile: 
    #     json.dump(entries, outfile, ensure_ascii=False, indent=2)
    
    ###############################

    # all_entries_of_vol = []
    # entry_nbr = 1
    # for vol_nbr, volume_path in enumerate(get_volumes(FIRST_ED_TEXT), start=1):
    #     try:
    #         for page_path in get_pages_of_volume(volume_path):
    #             entries, entry_nbr = extract_entries_from_page(page_path, entry_nbr, vol_nbr, 1)
    #             all_entries_of_vol += entries

    #         volume = volume_path.split('\\')[-1]
    #         with open(f"data/json/first_ed/{volume}.json", "w", encoding='utf-8') as outfile: 
    #             json.dump(all_entries_of_vol, outfile, ensure_ascii=False, indent=2)
    #         tot_entries = len(all_entries_of_vol)
    #         print(f"({volume}) AMOUNT OF ENTRIES CREATED: {tot_entries}")
    #         all_entries_of_vol.clear()
    #     except:
    #         sys.exit(f"Encountered error in: {page_path}")

    all_entries_of_vol = []
    entry_nbr = 1
    for vol_nbr, volume_path in enumerate(get_volumes(FOURTH_ED_TEXT), start=1):
        try:
            for page_path in get_pages_of_volume(volume_path):
                entries, entry_nbr = extract_entries_from_page(page_path, entry_nbr, vol_nbr, 4)
                all_entries_of_vol += entries

            volume = volume_path.split('\\')[-1]
            with open(f"data/json/fourth_ed/{volume}.json", "w", encoding='utf-8') as outfile: 
                json.dump(all_entries_of_vol, outfile, ensure_ascii=False, indent=2)
            tot_entries = len(all_entries_of_vol)
            print(f"TOTAL AMOUNT OF ENTRIES CREATED: {tot_entries}")
            all_entries_of_vol.clear()
        except:
            sys.exit(f"Encountered error in: {page_path}")