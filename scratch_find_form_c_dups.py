import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
name_col_c = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col_c = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col_c = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]
date_col_c = [col for col in df_c.columns if 'date of delivery' in str(col).lower()][0]

df_c['clean_mp_id'] = df_c[mp_col_c].astype(str).str.strip().str.replace('.0', '', regex=False)
df_c['clean_name'] = df_c[name_col_c].astype(str).str.strip().str.lower()
df_c['clean_husb'] = df_c[husb_col_c].astype(str).str.strip().str.lower()

# Check duplicates by MP ID (excluding dummy)
mp_counts = df_c[~df_c['clean_mp_id'].isin(['0', '00000000000', '0000000000', 'nan', 'no', 'none']) & (df_c['clean_mp_id'].str.len() > 5)]['clean_mp_id'].value_counts()
dup_mps = mp_counts[mp_counts > 1]
print("Duplicate MP IDs in Form C:")
for mp, cnt in dup_mps.items():
    rows = df_c[df_c['clean_mp_id'] == mp]
    print(f"\nMP {mp} (count {cnt}):")
    for idx, r in rows.iterrows():
        print(f"  Row {idx}: Name='{r['clean_name']}', Husb='{r['clean_husb']}', DelDate='{r[date_col_c]}', Time='{r['Timestamp']}'")

# Check duplicates by Name + Husband
name_husb_counts = df_c[df_c['clean_name'] != 'nan'][['clean_name', 'clean_husb']].value_counts()
dup_nh = name_husb_counts[name_husb_counts > 1]
print("\nDuplicate Name + Husband in Form C:")
for (n, h), cnt in dup_nh.items():
    rows = df_c[(df_c['clean_name'] == n) & (df_c['clean_husb'] == h)]
    print(f"\nName '{n}', Husb '{h}' (count {cnt}):")
    for idx, r in rows.iterrows():
        print(f"  Row {idx}: MP='{r['clean_mp_id']}', DelDate='{r[date_col_c]}', Time='{r['Timestamp']}'")
