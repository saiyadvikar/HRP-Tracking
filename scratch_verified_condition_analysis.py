import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')

# Clean names
def clean_n(s): return str(s).strip().lower() if pd.notna(s) else ""
def clean_mp(s):
    v = str(s).strip().replace('.0', '')
    if v in ['0', '00000000000', '0000000000', 'nan', 'no', 'none'] or v.replace('0', '') == '':
        return ""
    return v

df_a['clean_name'] = df_a.iloc[:, 2].apply(clean_n)
df_a['clean_husb'] = df_a.iloc[:, 3].apply(clean_n)
df_a['clean_mp'] = df_a.iloc[:, 1].apply(clean_mp)

df_b['clean_name'] = df_b.iloc[:, 2].apply(clean_n)
df_b['clean_husb'] = df_b.iloc[:, 3].apply(clean_n)
df_b['clean_mp'] = df_b.iloc[:, 1].apply(clean_mp)

# Match Form B to Form A
matches = {}
for b_idx, rb in df_b.iterrows():
    mp = rb['clean_mp']
    name = rb['clean_name']
    husb = rb['clean_husb']
    
    match_a = None
    if mp:
        m = df_a[df_a['clean_mp'] == mp]
        if len(m) > 0:
            match_a = m.index[0]
            
    if match_a is None and name:
        m = df_a[(df_a['clean_name'] == name) & (df_a['clean_husb'] == husb)]
        if len(m) > 0:
            match_a = m.index[0]
            
    if match_a is None and name:
        # substring or first name match
        m = df_a[(df_a['clean_name'].str.contains(name.split()[0])) & (df_a['clean_husb'] == husb)]
        if len(m) > 0:
            match_a = m.index[0]
            
    matches[b_idx] = match_a

print(f"Matched Form B visits: {sum(1 for v in matches.values() if v is not None)} / {len(df_b)}")

# Now verify condition for each matched visit:
# Col 6 in Form A is high-risk categories
hrp_col = df_a.columns[6]

cond_stats = {
    'Anemia': {'total_visits': 0, 'status_counts': {}, 'action_counts': {}},
    'PIH': {'total_visits': 0, 'status_counts': {}, 'action_counts': {}},
    'GDM': {'total_visits': 0, 'status_counts': {}, 'action_counts': {}},
    'SCD': {'total_visits': 0, 'status_counts': {}, 'action_counts': {}},
    'LSCS': {'total_visits': 0, 'status_counts': {}},
    'BOH': {'total_visits': 0, 'status_counts': {}},
    'Teen': {'total_visits': 0, 'status_counts': {}}
}

for b_idx, a_idx in matches.items():
    if a_idx is None: continue
    row_a = df_a.iloc[a_idx]
    row_b = df_b.iloc[b_idx]
    hrp_str = str(row_a[hrp_col]).lower()
    
    # 1. Severe Anemia
    if 'anemia' in hrp_str or 'anaemia' in hrp_str:
        st = str(row_b.iloc[26]).strip()
        act = str(row_b.iloc[27]).strip()
        if st and st != 'nan':
            cond_stats['Anemia']['total_visits'] += 1
            cond_stats['Anemia']['status_counts'][st] = cond_stats['Anemia']['status_counts'].get(st, 0) + 1
            if act and act != 'nan':
                cond_stats['Anemia']['action_counts'][act] = cond_stats['Anemia']['action_counts'].get(act, 0) + 1
                
    # 2. PIH
    if 'pih' in hrp_str or 'hypertension' in hrp_str:
        st = str(row_b.iloc[40]).strip()
        act = str(row_b.iloc[41]).strip()
        if st and st != 'nan':
            cond_stats['PIH']['total_visits'] += 1
            cond_stats['PIH']['status_counts'][st] = cond_stats['PIH']['status_counts'].get(st, 0) + 1
            if act and act != 'nan':
                cond_stats['PIH']['action_counts'][act] = cond_stats['PIH']['action_counts'].get(act, 0) + 1
                
    # 3. GDM
    if 'gdm' in hrp_str or 'diabetes' in hrp_str:
        st = str(row_b.iloc[51]).strip()
        act = str(row_b.iloc[52]).strip()
        if st and st != 'nan':
            cond_stats['GDM']['total_visits'] += 1
            cond_stats['GDM']['status_counts'][st] = cond_stats['GDM']['status_counts'].get(st, 0) + 1
            if act and act != 'nan':
                cond_stats['GDM']['action_counts'][act] = cond_stats['GDM']['action_counts'].get(act, 0) + 1
                
    # 4. SCD
    if 'scd' in hrp_str or 'sickle' in hrp_str:
        st = str(row_b.iloc[61]).strip()
        act = str(row_b.iloc[62]).strip()
        if st and st != 'nan':
            cond_stats['SCD']['total_visits'] += 1
            cond_stats['SCD']['status_counts'][st] = cond_stats['SCD']['status_counts'].get(st, 0) + 1
            if act and act != 'nan':
                cond_stats['SCD']['action_counts'][act] = cond_stats['SCD']['action_counts'].get(act, 0) + 1

    # 5. LSCS
    if 'lscs' in hrp_str or 'cesarean' in hrp_str:
        st = str(row_b.iloc[71]).strip()
        if st and st != 'nan':
            cond_stats['LSCS']['total_visits'] += 1
            cond_stats['LSCS']['status_counts'][st] = cond_stats['LSCS']['status_counts'].get(st, 0) + 1

    # 6. BOH
    if 'stillbirth' in hrp_str or 'neonatal' in hrp_str or 'death' in hrp_str or 'boh' in hrp_str:
        st = str(row_b.iloc[81]).strip()
        if st and st != 'nan':
            cond_stats['BOH']['total_visits'] += 1
            cond_stats['BOH']['status_counts'][st] = cond_stats['BOH']['status_counts'].get(st, 0) + 1

for c, s in cond_stats.items():
    print(f"\n================ Verified {c} Follow-ups ================")
    print(f"Total Verified Visits: {s['total_visits']}")
    print("Status counts:")
    for k, v in s['status_counts'].items():
        print(f"  {v:2d} | {k[:60]}")
    if 'action_counts' in s:
        print("Action counts:")
        for k, v in s['action_counts'].items():
            print(f"  {v:2d} | {k[:60]}")
