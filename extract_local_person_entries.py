from extract_entries import remove_tags
from local_data_handler import *
import regex as re

NAME = r"(?:\(?\p{Lu}\p{Ll}*\)?[ \t]?)"
PARTICLE = r"(?:\(?\p{Lu}?\p{Ll}*\)?[ \t]?)"
FIRST_ED_PATTERN = rf"^\d+\.[ \t]{NAME}{PARTICLE}*,[ \t]{NAME}{PARTICLE}*"
FOURTH_ED_PATTERN = rf"^{NAME}{PARTICLE}*,[ \t]\d+\.[ \t]{NAME}{PARTICLE}*"
FAMILY_MEMBER_PATTERN = re.compile(FIRST_ED_PATTERN + r"|" + FOURTH_ED_PATTERN)
FULL_NAME_PATTERN = re.compile(rf"^{NAME}{PARTICLE}*,[ \t]{NAME}{PARTICLE}*")

def space_even(text):
    res = re.sub("\s+", " ", text)
    res = re.sub("\s+,", ",", text)
    return res

def extract_family_member_entries(json, check_text=True):
    people = []
    for entry in json:
        new_entry = {
            "headword" : entry['headword'],
            "text" : entry['text'],
            "person" : 1
        }
        match = re.search(FAMILY_MEMBER_PATTERN, entry['headword'])
        if match:
            people.append(new_entry)
        elif check_text:
            text = remove_tags(entry['text'])
            text = space_even(text)
            match = re.search(FAMILY_MEMBER_PATTERN, text)
            if match:
                people.append(new_entry)
    return people

def extract_potential_people(json, check_text=True):
    candidates = []
    for entry in json:
        if len(entry['headword']) > 1:
            new_entry = {
            "headword" : entry['headword'],
            "text" : entry['text'],
            "person" : 1
            }
            match = re.search(FULL_NAME_PATTERN, entry['headword'])
            if match:
                candidates.append(new_entry)
            elif check_text:
                text = remove_tags(entry['text'])
                text = space_even(text)
                match = re.search(FULL_NAME_PATTERN, text)
                if match:
                    candidates.append(new_entry)
    return candidates

if __name__ == '__main__':
    # all_entries = []
    # for json_vol in get_json_vols_of_edition(FIRST_ED_JSON):
    #     content = load_json_vol(json_vol)
    #     people = extract_family_member_entries(content)
    #     # people = extract_potential_people(content)
    #     all_entries += people
    #     print(f" {json_vol} ... DONE")

    # with open(f"data/json/training/first_ed_families.json", "w", encoding="utf-8") as outfile:
    #     json.dump(all_entries, outfile, ensure_ascii=False, indent=2)

    # all_entries = []
    # for json_vol in get_json_vols_of_edition(FIRST_ED_JSON):
    #     content = load_json_vol(json_vol)
    #     # people = extract_family_member_entries(content)
    #     people = extract_potential_people(content)
    #     all_entries += people
    #     print(f" {json_vol} ... DONE")

    # with open(f"data/json/training/first_ed_potential_people.json", "w", encoding="utf-8") as outfile:
    #     json.dump(all_entries, outfile, ensure_ascii=False, indent=2)

    ##################

    all_entries = []
    for json_vol in get_jsons_of_dir(FOURTH_ED_JSON):
        content = load_json(json_vol)
        people = extract_family_member_entries(content)
        all_entries += people
        print(f" {json_vol} ... DONE")

    with open(f"data/json/training/fourth_ed_families.json", "w", encoding="utf-8") as outfile:
        json.dump(all_entries, outfile, ensure_ascii=False, indent=2)

    # all_entries = []
    # for json_vol in get_json_vols_of_edition(FOURTH_ED_JSON):
    #     content = load_json_vol(json_vol)
    #     # people = extract_family_member_entries(content)
    #     people = extract_potential_people(content, check_text=False)
    #     all_entries += people
    #     print(f" {json_vol} ... DONE")

    # with open(f"data/json/training/fourth_ed_potential_people.json", "w", encoding="utf-8") as outfile:
    #     json.dump(all_entries, outfile, ensure_ascii=False, indent=2)