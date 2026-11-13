import pandas as pd
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
mp_col_b = [col for col in df_b.columns if 'mp id' in str(col).lower()][0]
name_col_b = [col for col in df_b.columns if 'name' in str(col).lower() and 'anc' in str(col).lower()][0]

for idx, r in df_b.iterrows():
    mp = str(r[mp_col_b]).strip().replace('.0', '')
    if '26102195426' in mp:
        print(f"Row {idx} in Form B: Name: '{r[name_col_b]}' | MP: '{mp}'")
    if 'savin' in str(r[name_col_b]).lower() or 'sabin' in str(r[name_col_b]).lower():
        print(f"Name match in Form B Row {idx}: Name: '{r[name_col_b]}' | MP: '{mp}'")
