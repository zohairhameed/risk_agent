import sqlite3, json

conn = sqlite3.connect('risk.db')
suppliers = conn.execute("SELECT supplier_name, delivery_days, country FROM suppliers").fetchall()
supplier_text = "\n".join([f"{name}: {days} days from {location}" for name, days, location in suppliers])
outside = conn.execute("SELECT data FROM outside_data WHERE source='sanctions'").fetchone()[0]
sanctions_data = json.loads(outside)
outside_text = "\n".join([f"Supplier: {item['Supplier']}, Status: {item['Status']}" for item in sanctions_data])
conn.close()

print(supplier_text)
print(outside_text)