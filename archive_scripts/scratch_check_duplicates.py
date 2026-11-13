import pandas as pd
import json

# Let's inspect df_c for SAVINA, Babita, Kranti, Anita
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
name_col = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]
date_col = [col for col in df_c.columns if 'date of delivery' in str(col).lower()][0]

for name in ['SAVINA', 'Babita', 'Kranti', 'Anita', 'Sabina', 'Hansa']:
    print(f"\n--- Searching for {name} in Form C ---")
    for idx, r in df_c.iterrows():
        if name.lower() in str(r[name_col]).lower():
            print(f"Row {idx}: MP: {r[mp_col]} | Name: '{r[name_col]}' | Husband: '{r[husb_col]}' | Del Date: {r.get(date_col)} | Time: {r.get('Timestamp')}")
