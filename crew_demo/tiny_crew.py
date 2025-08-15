import sqlite3
import requests

# 1) Read supplier list
conn = sqlite3.connect('../risk.db')
cur = conn.cursor()
rows = cur.execute("SELECT supplier_name, delivery_days FROM suppliers").fetchall()
conn.close()

# 2) Build the prompt
prompt = (
    "For each supplier, write one short risk note (max 12 words).\n"
    + "\n".join(f"{name}: {days} days" for name, days in rows) + "\n\n"
    "Risk notes:"
)

# 3) Define the Ollama server URL and model name
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "gemma2:2b"

# 4) Generate text using Gemma 2B
response = requests.post(
    f"{OLLAMA_URL}/api/generate",
    json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
    timeout=60
)

# 5) Print the response
if response.status_code == 200:
    data = response.json()
    print("Raw model output:", data["response"])
else:
    print("Error:", response.status_code, response.text)