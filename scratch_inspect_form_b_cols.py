import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df_b = pd.read_excel('Form B_ Follow-up Visit Record (Responses).xlsx')
print(f"Total columns in Form B: {len(df_b.columns)}")

for i, col in enumerate(df_b.columns):
    col_str = str(col)
    if 'स्थिति' in col_str or 'कार्रवाई' in col_str or 'action' in col_str.lower() or 'status' in col_str.lower():
        print(f"Col {i}: {col_str}")
