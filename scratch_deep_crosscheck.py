import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

name_col_c = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col_c = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col_c = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]

rows_to_check = [0, 1, 15, 19, 29, 37, 43, 46, 48, 75]

print("=== CHECKING ROWS IN FORM A AND FORM B ===")
for r_idx in rows_to_check:
    rc = df_c.iloc[r_idx]
    c_name = str(rc[name_col_c]).strip().lower()
    c_husb = str(rc[husb_col_c]).strip().lower()
    c_mp = str(rc[mp_col_c]).strip().replace('.0', '')
    
    print(f"\n--- Checking Form C Row {r_idx}: Name='{c_name}', Husb='{c_husb}', MP='{c_mp}' ---")
    
    # Check Form A
    matches_a = []
    for a_idx, ra in df_a.iterrows():
        # Check all cells in ra for match
        row_str = " ".join([str(v).lower() for v in ra.values if pd.notna(v)])
        if c_mp and len(c_mp) > 5 and c_mp in row_str:
            matches_a.append((a_idx, 'MP ID match', ra.iloc[2], ra.iloc[3]))
        elif c_name != 'nan' and len(c_name) > 3 and c_name in row_str:
            matches_a.append((a_idx, 'Name substring', ra.iloc[2], ra.iloc[3]))
        elif c_husb != 'nan' and len(c_husb) > 3 and c_husb in row_str:
            matches_a.append((a_idx, 'Husb substring', ra.iloc[2], ra.iloc[3]))
            
    print(f"  Form A matches ({len(matches_a)}):")
    for m in matches_a[:5]:
        print(f"    Row {m[0]}: {m[1]} -> Name: '{m[2]}', Husb: '{m[3]}'")

    # Check Form B
    matches_b = []
    for b_idx, rb in df_b.iterrows():
        row_str = " ".join([str(v).lower() for v in rb.values if pd.notna(v)])
        if c_mp and len(c_mp) > 5 and c_mp in row_str:
            matches_b.append((b_idx, 'MP ID match', rb.iloc[2], rb.iloc[3]))
        elif c_name != 'nan' and len(c_name) > 3 and c_name in row_str:
            matches_b.append((b_idx, 'Name substring', rb.iloc[2], rb.iloc[3]))
        elif c_husb != 'nan' and len(c_husb) > 3 and c_husb in row_str:
            matches_b.append((b_idx, 'Husb substring', rb.iloc[2], rb.iloc[3]))
            
    print(f"  Form B matches ({len(matches_b)}):")
    for m in matches_b[:5]:
        print(f"    Row {m[0]}: {m[1]} -> Name: '{m[2]}', Husb: '{m[3]}'")
