import sqlite3, numpy as np

# 1) Read delivery days
conn = sqlite3.connect('risk.db')
days = [d[0] for d in conn.execute("SELECT delivery_days FROM suppliers").fetchall()]
conn.close()

worst = np.random.choice(days, 1000)
print(worst)