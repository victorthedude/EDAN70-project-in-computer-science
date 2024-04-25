from local_data_handler import *
from letter_dicts import FIRST_ED_LETTER_DICT, FOURTH_ED_LETTER_DICT, LETTERS
import random

first_ed = load_json("test/data/first_ed_potential_people.json")
fourth_ed = load_json("test/data/fourth_ed_potential_people.json")

DATASET_SAVE_LOC = "data/json/training/dataset.json"
LETTER_LIMIT = 10

# def prompt_save():
#     prompt = input("Save: ")
#     match prompt:
#         case "1":
#             return (True, False)
#         case "2":
#             return (False, True)
#         case "12" | "21":
#             return (True, True)
#         case _:
#             return (False, False)

def sample_entries_from_letter(letter_dict, letter, n=10):
    entries = random.sample(letter_dict[letter], n)
    def convert_entry(e):
        new_entry = {
            "text" : e['text'],
            "label" : 0
        }
        return new_entry
    entries = list(map(convert_entry, entries))
    return entries

def build_balanced_random(save_loc, n=10):
    entries = []
    for letter in LETTERS:
        entries += sample_entries_from_letter(FIRST_ED_LETTER_DICT, letter, n=n)
        entries += sample_entries_from_letter(FOURTH_ED_LETTER_DICT, letter, n=n)

    with open(save_loc, 'w', encoding='utf-8') as outfile:
        json.dump(entries, outfile, ensure_ascii=False, indent=2)

def count_person_entries(dataset):
    count = 0
    for e in dataset:
        if e['label'] == 1:
            count += 1
    print(f"Person Entries: {count}")
    print(f"Non-Persons Entries: {len(dataset)-count}")
    return count, len(dataset)-count

def manual_set_labels(dataset_json_path, start_index=-1):
    dataset = load_json(dataset_json_path)
    if start_index > 0:
        del dataset[start_index]['stop_index']
        dataset_enumerator = enumerate(dataset[start_index:], start=start_index)
    else:
        dataset_enumerator = enumerate(dataset, start=0)

    for i, entry in dataset_enumerator:
        print(f"CURRENTLY CHECKING ENTRY: {i}")
        print(entry)
        prompt = input("Is Person: ")
        if prompt == '1':
            dataset[i]['label'] = 1
        elif prompt == 'pause' or prompt == 'break' or prompt == 'stop' or prompt == 'save' or prompt == 'x':
            print(f"STOPPED AT: {i}")

            dataset[i]['stop_index'] = i

            with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
                json.dump(dataset, outfile, ensure_ascii=False, indent=2)
            break
    with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(dataset, outfile, ensure_ascii=False, indent=2)

def ask_add_person_entry(entry):
    print(entry)
    prompt = input("Add?: ")
    match prompt:
        case 'y' | '1':
            new_entry = {
                "text": entry['text'],
                "label": 1
            }
            return new_entry
        case 'pause' | 'break' | 'stop' | 'save' | 'x':
            return -1
        case _:
            return None

def manual_add_random_entry(dataset_json_path):
    dataset = load_json(dataset_json_path)
    person_count, non_person_count = count_person_entries(dataset)
    print(f"Person Entries: {person_count}")
    print(f"Non-Persons Entries: {non_person_count}")
    
    entries = []
    for letter in LETTERS:
        entry1 = sample_entries_from_letter(FIRST_ED_LETTER_DICT, letter, n=1)[0]
        new_entry1 = ask_add_person_entry(entry1)
        if new_entry1 == -1:
            break
        elif new_entry1:
            entries.append(new_entry1)
            non_person_count += 1
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")
        entry2 = sample_entries_from_letter(FOURTH_ED_LETTER_DICT, letter, n=1)[0]
        new_entry2 = ask_add_person_entry(entry2)
        if new_entry2 == -1:
            break
        elif new_entry2:
            entries.append(new_entry2)
            non_person_count += 1
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")

    dataset += entries

    with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(dataset, outfile, ensure_ascii=False, indent=2)
# build_balanced_random(DATASET_SAVE_LOC, n=LETTER_LIMIT)
# count_persons(DATASET_SAVE_LOC)

# build_balanced_random("data/json/training/test_dataset.json", n=4)
# manual_set_labels("data/json/training/test_dataset.json",206)
count_person_entries(load_json("data/json/training/test_dataset.json"))
manual_add_random_entry("data/json/training/test_dataset.json")