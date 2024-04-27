from util.local_data_handler import *

E1_A = 0
E1_B = 5124
E1_C = 11042
E1_D = 14780
E1_E = 18515
E1_F = 21348
E1_G = 25482
E1_H = 29156
E1_I = 33863
E1_J = 35492
E1_K = 36993
E1_L = 42637
E1_M = 46865
E1_N = 52126
E1_O = 54429
E1_P = 56068
E1_Q = 60975
E1_R = 61293
E1_S = 64854
E1_T = 73871
E1_U = 78431
E1_V = 79467
# E1_W = ...
E1_X = 83751
E1_Y = 83805
E1_Z = 84013
E1_Å = 84538
E1_Ä = 84881
E1_Ö = 85061
first_ed_letter_indices = [
    E1_A, E1_B, E1_C, E1_D, E1_E, E1_F, E1_G, E1_H, E1_I, E1_J, 
    E1_K, E1_L, E1_M, E1_N, E1_O, E1_P, E1_Q, E1_R, E1_S, E1_T, 
    E1_U, E1_V, E1_X, E1_Y, E1_Z, E1_Å, E1_Ä, E1_Ö
]

E4_A = 0
E4_B = 6841
E4_C = 15501
E4_D = 20257
E4_E = 24475
E4_F = 27870
E4_G = 32862
E4_H = 36950
E4_I = 41955
E4_J = 43676
E4_K = 45248
E4_L = 51746
E4_M = 56337
E4_N = 61986
E4_O = 64909
E4_P = 66646
E4_Q = 71161
E4_R = 71284
E4_S = 74847
E4_T = 84662
E4_U = 88263
E4_V = 89051
# E4_W = 
E4_X = 92477
E4_Y = 92516
E4_Z = 92670
E4_Å = 92869
E4_Ä = 93126
E4_Ö = 93299
fourth_ed_letter_indices = [
    E4_A, E4_B, E4_C, E4_D, E4_E, E4_F, E4_G, E4_H, E4_I, E4_J, 
    E4_K, E4_L, E4_M, E4_N, E4_O, E4_P, E4_Q, E4_R, E4_S, E4_T, 
    E4_U, E4_V, E4_X, E4_Y, E4_Z, E4_Å, E4_Ä, E4_Ö
]

LETTERS = "abcdefghijklmnopqrstuvxyzåäö" # 'w' not included
def build_letter_dict(ed_json, letter_indices):
    assert len(LETTERS) == len(letter_indices)

    all_entries = load_json(ed_json)
    letter_dict = {}
    for i in range(0, len(letter_indices)):
        letter = LETTERS[i]
        start = letter_indices[i]
        if i+1 < len(letter_indices):
            stop = letter_indices[i+1]
            entries_of_letter = all_entries[start:stop]
        else:
            entries_of_letter = all_entries[start:]
        letter_dict[letter] = entries_of_letter
    return letter_dict

FIRST_ED_LETTER_DICT = build_letter_dict("data/json/first_ed/first_ed.json", first_ed_letter_indices)
FOURTH_ED_LETTER_DICT = build_letter_dict("data/json/fourth_ed/fourth_ed.json", fourth_ed_letter_indices)