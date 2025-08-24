import requests, sqlite3, datetime, json

# 0) Setup
DB = 'risk.db'
TODAY = datetime.date.today().isoformat()

# 1) Example: MarineTraffic port congestion (fake URL for demo)
def fetch_port_delays():
    url = "https://api.marinetraffic.com/demo/port_delays"  # replace with real key later
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return {"Port": "Ningbo", "Delay_Hours": 12}

# 2) Example: OpenWeather typhoon risk (free key)
def fetch_weather():
    # Using a public demo response
    return {"City": "Shanghai", "Risk": "Low", "Date": TODAY}

# 3) Example: OFAC sanctions list (static CSV for demo)
def fetch_sanctions():
    return [{"Supplier": "Acme Bolts", "Status": "Country Sanctions"}]

# 4) Save everything to SQLite
conn = sqlite3.connect(DB)
conn.execute("CREATE TABLE IF NOT EXISTS outside_data (source TEXT, data TEXT, date TEXT)")
conn.execute("DELETE FROM outside_data")  # refresh daily
for name, func in [("port_delays", fetch_port_delays),
                   ("weather", fetch_weather),
                   ("sanctions", fetch_sanctions)]:
    conn.execute("INSERT INTO outside_data VALUES (?,?,?)",
                 (name, json.dumps(func()), TODAY))
conn.commit()
conn.close()

# 5) Confirmation
print("✅ Outside data stored")