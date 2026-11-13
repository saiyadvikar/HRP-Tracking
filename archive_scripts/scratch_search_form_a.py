import pandas as pd
import json

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
print(f"Total rows in Form A: {len(df_a)}")

name_col_a = [col for col in df_a.columns if 'name' in str(col).lower() and 'anc' in str(col).lower()][0]
husb_col_a = [col for col in df_a.columns if 'husband' in str(col).lower()][0]
mp_col_a = [col for col in df_a.columns if 'mp id' in str(col).lower()][0]

search_names = ['savina', 'sabina', 'babita', 'anita', 'reti', 'kranti', 'hansa', 'durga', 'bina', 'sajana', 'pinki']

for sn in search_names:
    matches = []
    for idx, r in df_a.iterrows():
        na = str(r[name_col_a]).lower()
        if sn in na:
            matches.append((idx, r[name_col_a], r[husb_col_a], str(r[mp_col_a])))
    print(f"\nSearch '{sn}' in Form A ({len(matches)} matches):")
    for m in matches:
        print(f"  Row {m[0]}: Name: '{m[1]}' | Husb: '{m[2]}' | MP: '{m[3]}'")

# Check MP 20233824208 from Row 0 in Form C
mp_search = '20233824208'
for idx, r in df_a.iterrows():
    if mp_search in str(r[mp_col_a]):
        print(f"\nFound MP {mp_search} in Form A Row {idx}: Name: '{r[name_col_a]}' | Husb: '{r[husb_col_a]}'")
