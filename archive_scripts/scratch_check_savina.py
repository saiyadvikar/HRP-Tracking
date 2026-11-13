import pandas as pd
df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
mp_col_a = [col for col in df_a.columns if 'mp id' in str(col).lower()][0]
name_col_a = [col for col in df_a.columns if 'name' in str(col).lower() and 'anc' in str(col).lower()][0]
husb_col_a = [col for col in df_a.columns if 'husband' in str(col).lower()][0]

for idx, r in df_a.iterrows():
    mp = str(r[mp_col_a]).strip().replace('.0', '')
    if '26102195426' in mp:
        print(f"Row 1 MP match in Form A Row {idx}: Name: '{r[name_col_a]}' | Husb: '{r[husb_col_a]}'")
