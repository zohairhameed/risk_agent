import pandas as pd

# 1) read the raw file
df = pd.read_csv('suppliers_raw.csv')

# 2) peek at the first 5 rows
print("Raw data:")
print(df.head())

# 3) drop completely empty rows
df = df.dropna(how='all')

# 4) fill any missing delivery_days with 0
df['delivery_days'] = df['delivery_days'].fillna(0)

# 5) change delivery_days to whole numbers
df['delivery_days'] = df['delivery_days'].astype(int)

# 6) remove rows where supplier name is blank
df = df[df['supplier_name'].notna()]

# 7) save the clean file
df.to_csv('clean_suppliers.csv', index=False)
print("✅ Saved clean_suppliers.csv")