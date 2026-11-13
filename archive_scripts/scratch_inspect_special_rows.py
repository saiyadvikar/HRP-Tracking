import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

for idx in [0, 15, 37, 43, 48]:
    r = df_c.iloc[idx]
    print(f"\n==================== ROW {idx} ====================")
    for col in df_c.columns:
        v = r[col]
        if pd.notna(v) and str(v).strip():
            print(f"  {col}: {v}")
