import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
r1 = df_c.iloc[1]
for k, v in r1.items():
    if pd.notna(v) and str(v).strip():
        print(f"  {k}: {v}")
