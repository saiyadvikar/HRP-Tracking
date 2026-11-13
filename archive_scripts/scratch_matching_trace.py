import pandas as pd
import json
from difflib import SequenceMatcher

data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = data['cases']
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

def clean_name(n):
    if not n or pd.isna(n): return ""
    return str(n).strip().lower()

def similarity(a, b):
    if not a or not b: return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

# Add clean_mp_id to df_c
df_c['clean_mp_id'] = df_c['MP ID'].astype(str).str.strip().str.replace('.0', '', regex=False)

matched_cases_per_row = {}
case_matches_count = {}

for idx, row_c in df_c.iterrows():
    mp_id_c = row_c['clean_mp_id']
    name_col = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
    husb_col = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
    name_c = clean_name(row_c[name_col])
    husb_c = clean_name(row_c[husb_col])
    
    match_case = None
    stage = ""
    # Stage 1: Clean MP ID match
    if mp_id_c and mp_id_c not in ['0', 'no', 'none']:
        for case in cases:
            if case['mp_id'] == mp_id_c:
                match_case = case
                stage = "Stage 1 (MP ID)"
                break
                
    # Stage 2: Exact Name & Husband Name match
    if not match_case and name_c:
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            if a_anc == name_c:
                if not husb_c or not a_husb or a_husb == husb_c or similarity(husb_c, a_husb) >= 0.65:
                    match_case = case
                    stage = "Stage 2 (Exact name + husb)"
                    break
                    
    # Stage 3: Fuzzy Name & Husband Name similarity match
    if not match_case and name_c:
        best_score = 0
        best_case = None
        for case in cases:
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            name_sim = similarity(name_c, a_anc)
            husb_sim = similarity(husb_c, a_husb) if (husb_c and a_husb) else 0.8
            is_sub = (name_c in a_anc or a_anc in name_c) and len(name_c) >= 3
            husb_sub = (husb_c in a_husb or a_husb in husb_c) and len(husb_c) >= 3 if (husb_c and a_husb) else False
            
            if (name_sim >= 0.75 or is_sub) and (husb_sim >= 0.60 or husb_sub):
                comb_score = name_sim + husb_sim
                if comb_score > best_score:
                    best_score = comb_score
                    best_case = case
        if best_case:
            match_case = best_case
            stage = f"Stage 3 (Fuzzy score {best_score:.2f})"

    if match_case:
        cid = match_case['id_a']
        cname = match_case['name']
        matched_cases_per_row[idx] = (cid, cname, stage)
        case_matches_count.setdefault(cid, []).append((idx, name_c, husb_c, stage))
    else:
        matched_cases_per_row[idx] = None

print("=== CASES MATCHED MULTIPLE TIMES ===")
for cid, rows in case_matches_count.items():
    if len(rows) > 1:
        print(f"Case ID {cid}: {rows}")

print("\n=== UNMATCHED ROWS IN FORM C ===")
for idx, m in matched_cases_per_row.items():
    if m is None:
        r = df_c.iloc[idx]
        print(f"Row {idx}: MP: {r['clean_mp_id']} | Name: '{r[name_col]}' | Husb: '{r[husb_col]}'")
