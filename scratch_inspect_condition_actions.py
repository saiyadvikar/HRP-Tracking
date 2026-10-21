import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = {c['id_a']: c for c in data['cases']}

cols = {
    'Anemia': (26, 27),
    'PIH': (40, 41),
    'GDM': (51, 52),
    'SCD': (61, 62),
    'LSCS': 71,
    'BOH': 81,
    'Teen': 93
}

print(f"Total rows in Form B: {len(df_b)}")

for cond, col_info in cols.items():
    print(f"\n==================== {cond} ====================")
    if isinstance(col_info, tuple):
        st_col, act_col = col_info
        st_name = df_b.columns[st_col]
        act_name = df_b.columns[act_col]
        print(f"Status Col: {st_name}")
        print(f"Action Col: {act_name}")
        
        st_vals = df_b[st_name].value_counts(dropna=False)
        print("\nStatus Values:")
        for v, cnt in st_vals.items():
            print(f"  {cnt:2d} | {v}")
            
        act_vals = df_b[act_name].value_counts(dropna=False)
        print("\nAction Values (non-null):")
        for v, cnt in act_vals.items():
            if pd.notna(v) and str(v).strip():
                print(f"  {cnt:2d} | {v}")
    else:
        st_col = col_info
        st_name = df_b.columns[st_col]
        print(f"Status Col: {st_name}")
        st_vals = df_b[st_name].value_counts(dropna=False)
        for v, cnt in st_vals.items():
            print(f"  {cnt:2d} | {v}")
