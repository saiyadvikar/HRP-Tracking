import pandas as pd
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

name_col_c = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col_c = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col_c = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]
date_col_c = [col for col in df_c.columns if 'date of delivery' in str(col).lower()][0]

name_col_a = [col for col in df_a.columns if 'name' in str(col).lower() and 'anc' in str(col).lower()][0]
husb_col_a = [col for col in df_a.columns if 'husband' in str(col).lower()][0]
mp_col_a = [col for col in df_a.columns if 'mp id' in str(col).lower()][0]

print(f"Total rows in Form C: {len(df_c)}")
print(f"Total rows in Form A: {len(df_a)}")
print(f"Total rows in Form B: {len(df_b)}")

# Let's inspect each of the 77 rows of Form C:
for idx, r in df_c.iterrows():
    c_name = str(r[name_col_c]).strip()
    c_husb = str(r[husb_col_c]).strip()
    c_mp = str(r[mp_col_c]).strip().replace('.0', '')
    c_date = str(r.get(date_col_c))[:10]
    c_time = str(r.get('Timestamp'))[:19]
    print(f"Row {idx:2d} | MP: {c_mp:12s} | Name: {c_name:15s} | Husb: {c_husb:15s} | Del Date: {c_date} | Submitted: {c_time}")
