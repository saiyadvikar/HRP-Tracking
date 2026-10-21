import pandas as pd
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
print("Row 0:")
for k, v in df_c.iloc[0].items():
    if pd.notna(v) and str(v).strip():
        print(f"  {k}: {v}")
