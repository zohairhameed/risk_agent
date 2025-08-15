import sqlite3
import pandas as pd

# 1. Read the cleaned CSV
df = pd.read_csv('clean_suppliers.csv')

# 2. Connect to the database
conn = sqlite3.connect('risk.db')

# 3. Push the table into the database
df.to_sql('suppliers', conn, if_exists='replace', index=False)

# 4. Quick check: count rows
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM suppliers")
print("Rows in database:", cur.fetchone()[0])

# 5. Close the connection
conn.close()