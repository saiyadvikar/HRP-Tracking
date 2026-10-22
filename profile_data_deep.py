import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_a = pd.read_excel('Form A_ Identification Record (Responses).xlsx')
df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
df_c = pd.read_excel('Form C_ Delivery Outcome Record (Responses).xlsx')

print("Form C Place of delivery:", df_c.iloc[:, 6].value_counts().to_dict())
print("Form C Type of delivery:", df_c.iloc[:, 7].value_counts().to_dict())
print("Form C Planned vs Actual Facility:", df_c.iloc[:, 9].value_counts().to_dict())
print("Form C Baby Alive:", df_c.iloc[:, 31].value_counts().to_dict())
print("Form C Birth Weight Categories:", df_c.iloc[:, 33].value_counts().to_dict())
print("Form C SNCU Transfer:", df_c.iloc[:, 36].value_counts().to_dict())
print("Form C Skin-to-skin:", df_c.iloc[:, 38].value_counts().to_dict())
print("Form C Breastfeeding <1h:", df_c.iloc[:, 39].value_counts().to_dict())
print("Form C Vitamin K:", df_c.iloc[:, 40].value_counts().to_dict())
print("Form C Partograph:", df_c.iloc[:, 26].value_counts().to_dict())
print("Form C Oxytocin within 1m:", df_c.iloc[:, 27].value_counts().to_dict())
print("Form C Birth Companion:", df_c.iloc[:, 28].value_counts().to_dict())
print("Form C Abuse/Disrespect:", df_c.iloc[:, 29].value_counts().to_dict())
