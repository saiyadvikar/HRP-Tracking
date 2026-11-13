import pandas as pd
import json
import sys
from difflib import SequenceMatcher
sys.stdout.reconfigure(encoding='utf-8')

# Run current generate_analysis_data.py loading logic
data = json.load(open('dashboard_data.json', encoding='utf-8'))
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

def clean_str(s): return str(s).strip() if pd.notna(s) else ""
def clean_name(n): return str(n).strip().lower() if pd.notna(n) else ""
def similarity(a, b):
    if not a or not b: return 0.0
    return SequenceMatcher(None, str(a).lower().strip(), str(b).lower().strip()).ratio()

def is_valid_mp(mp):
    if not mp or pd.isna(mp): return False
    v = str(mp).strip().replace('.0', '').lower()
    if v in ['', '0', 'nan', 'none', 'no', 'null']: return False
    if v.replace('0', '') == '': return False # all zeroes
    if len(v) < 6: return False
    return True

df_c['clean_mp_id'] = df_c['MP ID'].astype(str).str.strip().str.replace('.0', '', regex=False)

# Re-run matching against original cases
cases = [c for c in data['cases'] if not c.get('is_unlinked_delivery')]
# reset delivery
for c in cases:
    c['delivery'] = None

matched_c_count = 0
unlinked_count = 0

for idx, row_c in df_c.iterrows():
    mp_id_c = row_c['clean_mp_id']
    name_c = clean_name(row_c.get('ANC Name (गर्भवती महिला का नाम)'))
    husb_c = clean_name(row_c.get('Husband Name (पति का नाम)'))
    
    match_case = None
    
    # Stage 1: Valid MP ID match
    if is_valid_mp(mp_id_c):
        for case in cases:
            if is_valid_mp(case['mp_id']) and case['mp_id'] == mp_id_c and case['delivery'] is None:
                match_case = case
                break
                
    # Stage 2: Exact Name & Husband match
    if not match_case and name_c:
        for case in cases:
            if case['delivery'] is not None: continue
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            if a_anc == name_c:
                if not husb_c or not a_husb or a_husb == husb_c or similarity(husb_c, a_husb) >= 0.65:
                    match_case = case
                    break
                    
    # Stage 3: Fuzzy Name match (require husband if low name sim)
    if not match_case and name_c:
        best_score = 0
        best_case = None
        for case in cases:
            if case['delivery'] is not None: continue
            a_anc = clean_name(case['name'])
            a_husb = clean_name(case['husband_name'])
            name_sim = similarity(name_c, a_anc)
            husb_sim = similarity(husb_c, a_husb) if (husb_c and a_husb) else (0.8 if name_sim >= 0.9 else 0.0)
            is_sub = (name_c in a_anc or a_anc in name_c) and len(name_c) >= 4
            husb_sub = (husb_c in a_husb or a_husb in husb_c) and len(husb_c) >= 3 if (husb_c and a_husb) else False
            
            if (name_sim >= 0.80 or is_sub) and (husb_sim >= 0.60 or husb_sub):
                comb_score = name_sim + husb_sim
                if comb_score > best_score:
                    best_score = comb_score
                    best_case = case
        if best_case and best_score >= 1.4:
            match_case = best_case

    del_data = {"id_c": int(idx), "name": name_c, "date": str(row_c.get('Date of delivery'))[:10]}
    
    if match_case:
        match_case['delivery'] = del_data
        matched_c_count += 1
    else:
        unlinked_count += 1
        # Create unlinked case
        new_case = {
            "id_a": 1000 + int(idx),
            "mp_id": mp_id_c if is_valid_mp(mp_id_c) else f"C-{idx+1:02d}",
            "name": clean_str(row_c.get('ANC Name (गर्भवती महिला का नाम)')) or f"Delivery Record #{idx+1}",
            "husband_name": clean_str(row_c.get('Husband Name (पति का नाम)')) or "-",
            "delivery": del_data,
            "is_unlinked_delivery": True
        }
        cases.append(new_case)

all_del = [c for c in cases if c.get('delivery')]
print(f"Total Form C rows: {len(df_c)}")
print(f"Directly matched to Form A cases: {matched_c_count}")
print(f"Unlinked / Re-submission delivery cases created: {unlinked_count}")
print(f"Total cases with delivery in cases array: {len(all_del)}")
