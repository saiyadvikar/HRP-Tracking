import pandas as pd
import json

data = json.load(open('dashboard_data.json', encoding='utf-8'))
cases = data['cases']
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')
df_c['clean_mp_id'] = df_c['MP ID'].astype(str).str.strip().str.replace('.0', '', regex=False)

c6 = [c for c in cases if c['id_a'] == 6][0]
print(f"Case ID 6 in cases: Name: '{c6['name']}' | Husb: '{c6['husband_name']}' | MP: '{c6['mp_id']}'")

print(f"Row 11 in Form C: MP: '{df_c.iloc[11]['clean_mp_id']}' | Name: '{df_c.iloc[11].get('ANC Name (गर्भवती महिला का नाम)')}'")
print(f"Row 55 in Form C: MP: '{df_c.iloc[55]['clean_mp_id']}' | Name: '{df_c.iloc[55].get('ANC Name (गर्भवती महिला का नाम)')}'")
print(f"Row 60 in Form C: MP: '{df_c.iloc[60]['clean_mp_id']}' | Name: '{df_c.iloc[60].get('ANC Name (गर्भवती महिला का नाम)')}'")
