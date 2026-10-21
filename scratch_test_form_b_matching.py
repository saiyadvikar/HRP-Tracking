import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')

def clean_str(s): return str(s).strip() if pd.notna(s) else ""
def clean_n(s): return str(s).strip().lower() if pd.notna(s) else ""
def is_valid_mp(mp):
    if not mp: return False
    v = str(mp).strip().replace('.0', '').lower()
    if v in ['', '0', 'nan', 'none', 'no', 'null']: return False
    if v.replace('0', '') == '': return False # all zeroes like 00000000000
    if len(v) < 6: return False
    return True

df_a['clean_name'] = df_a.iloc[:, 2].apply(clean_n)
df_a['clean_husb'] = df_a.iloc[:, 3].apply(clean_n)
df_a['raw_mp'] = df_a.iloc[:, 1].apply(clean_str)

df_b['clean_name'] = df_b.iloc[:, 2].apply(clean_n)
df_b['clean_husb'] = df_b.iloc[:, 3].apply(clean_n)
df_b['raw_mp'] = df_b.iloc[:, 1].apply(clean_str)

matched_b = {}
for b_idx, rb in df_b.iterrows():
    mp_b = rb['raw_mp']
    name_b = rb['clean_name']
    husb_b = rb['clean_husb']
    
    match_a = None
    if is_valid_mp(mp_b):
        m = df_a[df_a['raw_mp'] == mp_b]
        if len(m) > 0:
            match_a = m.index[0]
            
    if match_a is None and name_b:
        m = df_a[(df_a['clean_name'] == name_b) & (df_a['clean_husb'] == husb_b)]
        if len(m) > 0:
            match_a = m.index[0]
            
    if match_a is None and name_b:
        # substring
        for a_idx, ra in df_a.iterrows():
            na = ra['clean_name']
            ha = ra['clean_husb']
            if (name_b in na or na in name_b) and (not husb_b or not ha or husb_b in ha or ha in husb_b):
                match_a = a_idx
                break
                
    matched_b[b_idx] = match_a

matched_count = sum(1 for v in matched_b.values() if v is not None)
print(f"Properly matched Form B visits: {matched_count} / {len(df_b)}")
for b_idx, a_idx in matched_b.items():
    if a_idx is None:
        rb = df_b.iloc[b_idx]
        print(f"Unmatched Form B row {b_idx}: Name='{rb['clean_name']}', Husb='{rb['clean_husb']}', MP='{rb['raw_mp']}'")
