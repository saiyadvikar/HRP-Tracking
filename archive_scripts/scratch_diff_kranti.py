import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
r37 = df_c.iloc[37]
r48 = df_c.iloc[48]

diffs = []
for col in df_c.columns:
    v37 = str(r37[col])
    v48 = str(r48[col])
    if v37 != v48:
        diffs.append((col, v37, v48))

print(f"Total differences between Row 37 and Row 48: {len(diffs)}")
for d in diffs:
    print(f"Col '{d[0]}':\n  Row 37: '{d[1]}'\n  Row 48: '{d[2]}'\n")
