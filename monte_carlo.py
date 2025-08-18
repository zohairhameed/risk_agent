import sqlite3, numpy as np

# 1) Read delivery days
conn = sqlite3.connect('../risk.db')
days = [d[0] for d in conn.execute("SELECT delivery_days FROM suppliers").fetchall()]
conn.close()

# 2) Roll the dice 1,000 times
worst = int(np.percentile(np.random.choice(days, 1000), 95))
print("95 % worst delay =", worst, "days")

import matplotlib.pyplot as plt
plt.hist(np.random.choice(days, 1000), bins=5, color='skyblue')
plt.title("Delivery Delay Simulation"); plt.show()