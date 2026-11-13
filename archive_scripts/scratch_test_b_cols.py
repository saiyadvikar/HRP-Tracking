import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')

def get_col(keywords):
    for col in df_b.columns:
        if all(k in str(col) for k in keywords):
            return col
    return None

print("Anemia status col:", get_col(['स्थिति', 'एनीमिया']))
print("Anemia action col:", get_col(['कार्रवाई', 'एनीमिया']) or get_col(['कार्रवाई', 'Done by FC']) or df_b.columns[27])
print("PIH status col:", get_col(['स्थिति', 'पीआईएच']))
print("PIH action col:", df_b.columns[41])
print("GDM status col:", get_col(['स्थिति', 'जीडीएम']))
print("GDM action col:", df_b.columns[52])
print("SCD status col:", get_col(['स्थिति', 'एससीडी']))
print("SCD action col:", get_col(['स्थिति स्थिर नहीं', 'कार्रवाई']) or df_b.columns[62])
