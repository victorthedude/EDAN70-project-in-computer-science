from util.local_data_handler import *
from util.letter_dicts import FIRST_ED_LETTER_DICT, FOURTH_ED_LETTER_DICT, LETTERS
import random

LETTER_LIMIT = 10

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

def build_balanced_random(save_loc, n=10, training_data=None):
    entries = []
    if training_data:
        training_texts = set([entry['text'] for entry in training_data]) # make sure there is no duplicate text in training and validation data
        for letter in LETTERS:
            e1s = [entry for entry in sample_entries_from_letter(FIRST_ED_LETTER_DICT, letter, n=n) if entry['text'] not in training_texts]
            e2s = [entry for entry in sample_entries_from_letter(FOURTH_ED_LETTER_DICT, letter, n=n) if entry['text'] not in training_texts]
            while len(e1s) < n and len(e2s) < n:
                if len(e1s) < n:
                    e1s = [entry for entry in sample_entries_from_letter(FIRST_ED_LETTER_DICT, letter, n=n) if entry['text'] not in training_texts]
                if len(e2s) < n:
                    e2s = [entry for entry in sample_entries_from_letter(FOURTH_ED_LETTER_DICT, letter, n=n) if entry['text'] not in training_texts]
            entries += e1s
            entries += e2s
    else:
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

def manual_set_labels(dataset_json_path):
    dataset = load_json(dataset_json_path)
    person_count, non_person_count = count_person_entries(dataset)

    start_index = 0
    for entry in dataset:
        if 'stop_index' in entry.keys():
            start_index = entry['stop_index']

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
            person_count += 1
            non_person_count -= 1
        elif prompt == 'pause' or prompt == 'break' or prompt == 'stop' or prompt == 'save' or prompt == 'x':
            print(f"STOPPED AT: {i}")

            dataset[i]['stop_index'] = i

            with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
                json.dump(dataset, outfile, ensure_ascii=False, indent=2)
            return
        
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")

    with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(dataset, outfile, ensure_ascii=False, indent=2)

def ask_add_entry(entry):
    print(entry)
    prompt = input("label (0==non-person, 1==person): ")
    match prompt:
        case '1':
            new_entry = {
                "text": entry['text'],
                "label": 1
            }
            return new_entry
        case '0':
            new_entry = {
                "text": entry['text'],
                "label": 0
            }
            return new_entry
        case 'pause' | 'break' | 'stop' | 'save' | 'x':
            return -1
        case _:
            return None

def manual_add_random_entry_from_letter_dict(dataset_json_path):
    dataset = load_json(dataset_json_path)
    person_count, non_person_count = count_person_entries(dataset)
    print(f"Person Entries: {person_count}")
    print(f"Non-Persons Entries: {non_person_count}")
    
    entries = []
    for letter in LETTERS:
        entry1 = sample_entries_from_letter(FIRST_ED_LETTER_DICT, letter, n=1)[0]
        new_entry1 = ask_add_entry(entry1)
        if new_entry1 == -1:
            break
        elif new_entry1:
            entries.append(new_entry1)
            non_person_count += 1
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")
        entry2 = sample_entries_from_letter(FOURTH_ED_LETTER_DICT, letter, n=1)[0]
        new_entry2 = ask_add_entry(entry2)
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

def manual_add_random_entry_from_json(dataset_json_path, first_ed_json, fourth_ed_json):
    dataset = load_json(dataset_json_path)

    person_count, non_person_count = count_person_entries(dataset)
    print(f"Person Entries: {person_count}")
    print(f"Non-Persons Entries: {non_person_count}")

    text_entry_set = set([entry['text'] for entry in dataset])
    
    entries = []
    while True:
        entry1 = random.choice(first_ed_json)
        new_entry1 = ask_add_entry(entry1)
        if new_entry1 == -1:
            break
        elif new_entry1 and new_entry1['text'] not in text_entry_set:
            entries.append(new_entry1)
            if new_entry1['label'] == 0:
                non_person_count += 1
            elif new_entry1['label'] == 1:
                person_count += 1
            text_entry_set.add(new_entry1['text'])
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")

        entry2 = random.choice(fourth_ed_json)
        new_entry2 = ask_add_entry(entry2)
        if new_entry2 == -1:
            break
        elif new_entry2 and new_entry2['text'] not in text_entry_set:
            entries.append(new_entry2)
            if new_entry2['label'] == 0:
                non_person_count += 1
            elif new_entry2['label'] == 1:
                person_count += 1
            text_entry_set.add(new_entry2['text'])
        print(f"Person Entries: {person_count}")
        print(f"Non-Persons Entries: {non_person_count}")

    dataset += entries

    with open(dataset_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(dataset, outfile, ensure_ascii=False, indent=2)


DATASET_SAVE_LOC = "data/json/training/dataset_1_validation.json"
# prompt = input("Create new dataset? (y/n): ")
# if prompt == "y":
#     build_balanced_random(DATASET_SAVE_LOC, n=2, training_data=load_json("data/json/training/dataset_1_training.json"))
#     manual_set_labels(DATASET_SAVE_LOC)
# else:
#     manual_set_labels(DATASET_SAVE_LOC)
# count_persons(DATASET_SAVE_LOC)

# build_balanced_random("data/json/training/test_dataset.json", n=4)
# manual_set_labels("data/json/training/test_dataset.json",206)
# count_person_entries(load_json("data/json/training/test_dataset.json"))
# manual_add_random_entry_from_letter_dict("data/json/training/test_dataset.json")

# json1 = load_json("test/data/first_ed_potential_people.json")
# json2 = load_json("test/data/fourth_ed_potential_people.json")
# json1 = load_json("data/json/first_ed/first_ed.json")
# json2 = load_json("data/json/fourth_ed/fourth_ed.json")
# manual_add_random_entry_from_json("data/json/training/test_dataset.json", json1, json2)