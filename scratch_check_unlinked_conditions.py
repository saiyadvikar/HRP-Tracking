import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
name_col_c = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col_c = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col_c = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]

rows = [0, 1, 15, 19, 29, 43, 46, 75]

for idx in rows:
    r = df_c.iloc[idx]
    print(f"\n--- Row {idx}: Name='{r[name_col_c]}', Husb='{r[husb_col_c]}', MP='{r[mp_col_c]}' ---")
    print(f"  Facility: {r.get('Name of facility where delivery occurred- (प्रसव होने वाले स्थान का विशिष्ट नाम)') or r.get('Place of delivery-(डिलिवरी का स्थान)')}")
    print(f"  Delivery Type: {r.get('Type of delivery- (डिलिवरी का स्थान)')}")
    print(f"  Hb: {r.get('HB on Admission')}, Anemia St: {r.get('Status at delivery — Severe Anemia')}")
    print(f"  BP: {r.get('BP on Admission')}, PIH St: {r.get('Status at delivery — PIH')}")
    print(f"  SCD St: {r.get('Status at delivery — SCD- (प्रसव के समय स्थिति — एससीडी)')}")
    print(f"  GDM St: {r.get('Status at delivery — GDM')}")
    print(f"  Overall: {r.get('OVERALL HRP status at delivery (across all identified conditions)- (प्रसव के समय समग्र एचआरपी स्थिति (सभी पहचाने गए स्थितियों में)')}")
    print(f"  Remarks: {r.get('Any gaps or concerns during delivery / immediate newborn period- (प्रसव/नवजात शिशु के तत्काल बाद की अवधि के दौरान किसी भी प्रकार की कमी या चिंताएँ।)')}")
