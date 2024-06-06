import regex as re

NAME = r"(?:\(?\p{Lu}\p{Ll}*\)?[ \t]?)"
PARTICLE = r"(?:\(?\p{Lu}?\p{Ll}*\)?[ \t]?)"
FIRST_ED_PATTERN = rf"^\d+\.[ \t]{NAME}{PARTICLE}*,[ \t]{NAME}{PARTICLE}*$"
FOURTH_ED_PATTERN = rf"{NAME}{PARTICLE}*,[ \t]\d+\.[ \t]{NAME}{PARTICLE}*"
FAMILY_MEMBER_PATTERN = re.compile(FIRST_ED_PATTERN + r"|" + FOURTH_ED_PATTERN)
FULL_NAME_PATTERN = re.compile(rf"^{NAME}{PARTICLE}*,[ \t]{NAME}{PARTICLE}*")

def remove_tags(string):
    return re.sub(r'<\/?[^>]+>|\[[^\]]+\]', '', string) # removes ALL tags + phonetics fluff

def normalize_text(text): # remove spaceing + punctuation + aprostrophes
    return re.sub(r"[.,' \t]", "", text)

def split_even(text) -> list[str]: # split between words + take care of any accidental double spacing or lingering punctuation
    res = re.sub("\s+", " ", text)
    res = list(filter(bool, [word.strip(' ,.') for word in res.split(' ')]))
    return res

def space_even(text): # normalize spacing - remove any double spacing
    res = re.sub("\s+", " ", text)
    res = re.sub("\s+,", ",", text)
    return res

def find_members_of_family(index):
    matches = []
    for headword in index:
        match = re.search(FAMILY_MEMBER_PATTERN, headword)
        if match:
            matches.append(match.group(0))
    # if matches:
    #     print(matches)
    return matches