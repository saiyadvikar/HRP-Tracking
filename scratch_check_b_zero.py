import pandas as pd
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
mp_col_b = [col for col in df_b.columns if 'mp id' in str(col).lower()][0]
zero_mps = df_b[df_b[mp_col_b].astype(str).str.contains('^0+$', regex=True)]
print(f"Zero MP IDs in Form B: {len(zero_mps)}")
for idx, r in zero_mps.iterrows():
    print(f"  Row {idx}: Name: {r.iloc[2]} | Husb: {r.iloc[3]} | MP: {r[mp_col_b]}")
