import sqlite3, subprocess, requests, json

# 0) Setup
MODEL_NAME = "gemma2:2b"
OLLAMA_URL = "http://localhost:11434"

# 1) Ensure model is downloaded
result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
if MODEL_NAME not in result.stdout:
    print(f"Model {MODEL_NAME} not found. Pulling now...")
    subprocess.run(["ollama", "pull", MODEL_NAME])
    print(f"Model {MODEL_NAME} downloaded.")

# 2) Read supplier list
conn = sqlite3.connect('risk.db')
suppliers = conn.execute("SELECT supplier_name, delivery_days, country FROM suppliers").fetchall()
supplier_text = "\n".join([f"{name}: {days} days from {location}" for name, days, location in suppliers])
outside = conn.execute("SELECT data FROM outside_data WHERE source='sanctions'").fetchone()[0]
sanctions_data = json.loads(outside)
outside_text = "\n".join([f"Supplier: {item['Supplier']}, Status: {item['Status']}" for item in sanctions_data])
conn.close()

# 3) Build the prompt
prompt = (
    "Supplier data:\n"
    + supplier_text + "\n\n"
    "Sanctions:" + outside_text + "\n\n"
    "For each supplier, write one concise risk note (≤12 words)."
)

# 4) Generate text using Gemma 2B
response = requests.post(
    f"{OLLAMA_URL}/api/generate",
    json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
    timeout=120
)

# 5) Print the response
if response.status_code == 200:
    data = response.json()
    print(response.json()["response"])
else:
    print("Error:", response.status_code, response.text)
