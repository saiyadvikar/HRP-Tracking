import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

def clean_str(s): return str(s).strip() if pd.notna(s) else ""
def clean_n(s): return str(s).strip().lower() if pd.notna(s) else ""
def is_valid_mp(mp):
    if not mp or pd.isna(mp): return False
    v = str(mp).strip().replace('.0', '').lower()
    if v in ['', '0', 'nan', 'none', 'no', 'null']: return False
    if v.replace('0', '') == '': return False
    if len(v) < 6: return False
    return True

df_a['clean_name'] = df_a.iloc[:, 2].apply(clean_n)
df_a['clean_husb'] = df_a.iloc[:, 3].apply(clean_n)
df_a['clean_mp'] = df_a.iloc[:, 1].apply(lambda x: str(x).strip().replace('.0', '') if is_valid_mp(x) else "")

df_c['clean_name'] = df_c.iloc[:, 2].apply(clean_n)
df_c['clean_husb'] = df_c.iloc[:, 3].apply(clean_n)
df_c['clean_mp'] = df_c.iloc[:, 1].apply(lambda x: str(x).strip().replace('.0', '') if is_valid_mp(x) else "")

matched_c = {}
used_cases = set()

for c_idx, rc in df_c.iterrows():
    mp_c = rc['clean_mp']
    name_c = rc['clean_name']
    husb_c = rc['clean_husb']
    
    match_a = None
    # Stage 1: Valid MP ID
    if mp_c:
        m = df_a[df_a['clean_mp'] == mp_c]
        if len(m) > 0 and m.index[0] not in used_cases:
            match_a = m.index[0]
            
    # Stage 2: Exact Name & Husband
    if match_a is None and name_c:
        m = df_a[(df_a['clean_name'] == name_c) & (df_a['clean_husb'] == husb_c)]
        for cand in m.index:
            if cand not in used_cases:
                match_a = cand
                break
                
    # Stage 3: Substring Name with Husband
    if match_a is None and name_c and husb_c:
        for a_idx, ra in df_a.iterrows():
            if a_idx in used_cases: continue
            na = ra['clean_name']
            ha = ra['clean_husb']
            if (name_c in na or na in name_c) and (husb_c in ha or ha in husb_c):
                match_a = a_idx
                break
                
    if match_a is not None:
        used_cases.add(match_a)
        matched_c[c_idx] = (match_a, 'matched', df_a.iloc[match_a]['clean_name'])
    else:
        matched_c[c_idx] = (None, 'unlinked', name_c)

print(f"Total Form C rows: {len(df_c)}")
matched_count = sum(1 for v in matched_c.values() if v[0] is not None)
unlinked_count = sum(1 for v in matched_c.values() if v[0] is None)
print(f"Matched directly to Form A cases: {matched_count}")
print(f"Unlinked / Re-submission delivery rows: {unlinked_count}")
print(f"Sum = {matched_count + unlinked_count} == {len(df_c)}")

print("\n--- Unlinked Rows List ---")
for c_idx, v in matched_c.items():
    if v[0] is None:
        rc = df_c.iloc[c_idx]
        print(f"Row {c_idx:2d}: Name='{rc.iloc[2]}', Husb='{rc.iloc[3]}', MP='{rc.iloc[1]}', DelDate='{rc.iloc[4]}'")
