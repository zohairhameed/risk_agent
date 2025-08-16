import sqlite3, numpy as np

conn = sqlite3.connect('../risk.db')
days = [d[0] for d in conn.execute("SELECT delivery_days FROM suppliers").fetchall()]
conn.close()

trials = 1000
sim = np.random.choice(days, size=trials)
p95 = np.percentile(sim, 95)

print(f"95 % worst delay = {int(p95)} days")