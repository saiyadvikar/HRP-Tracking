import pandas as pd
import json

data = json.load(open('dashboard_data.json', encoding='utf-8'))
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

matched_id_cs = {}
for c in data['cases']:
    if c.get('delivery'):
        id_c = c['delivery']['id_c']
        matched_id_cs[id_c] = c

unlinked_id_cs = {u['id_c']: u for u in data.get('unlinked_deliveries', [])}

print(f'Total df_c rows: {len(df_c)}')
print(f'Matched id_c count: {len(matched_id_cs)}')
print(f'Unlinked id_c count: {len(unlinked_id_cs)}')

missing_id_cs = [i for i in range(len(df_c)) if i not in matched_id_cs and i not in unlinked_id_cs]
print(f'Missing id_cs count: {len(missing_id_cs)}: {missing_id_cs}')

name_col = [col for col in df_c.columns if 'anc name' in str(col).lower()][0]
husb_col = [col for col in df_c.columns if 'husband' in str(col).lower()][0]
mp_col = [col for col in df_c.columns if 'mp id' in str(col).lower()][0]

for i in missing_id_cs:
    row = df_c.iloc[i]
    print(f"Missing Row {i}: MP: {row[mp_col]} | Name: {row[name_col]} | Husband: {row[husb_col]}")

print("\n--- Now let's inspect the 7 Unlinked rows ---")
for id_c, u in unlinked_id_cs.items():
    print(f"Unlinked Row {id_c}: MP: {u.get('mp_id')} | Name: {u.get('name')} | Husband: {u.get('husband_name')}")
