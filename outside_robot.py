import sqlite3
import subprocess
import requests

# 0) Ensure model is downloaded
MODEL_NAME = "gemma2:2b"
OLLAMA_URL = "http://localhost:11434"

# Check if model exists locally
result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
if MODEL_NAME not in result.stdout:
    print(f"Model {MODEL_NAME} not found. Pulling now...")
    subprocess.run(["ollama", "pull", MODEL_NAME])
    print(f"Model {MODEL_NAME} downloaded.")

# 1) Read supplier list
conn = sqlite3.connect('../risk.db')
suppliers = conn.execute("SELECT supplier_name, delivery_days FROM suppliers").fetchall()
outside = conn.execute("SELECT data FROM outside_data WHERE source='port_delays'").fetchone()[0]
conn.close()

# 2) Build the prompt
prompt = (
    "Suppliers and delivery days:\n"
    + "\n".join(f"{n}: {d} days" for n, d in suppliers) + "\n\n"
    f"Port delays: {outside}\n\n"
    "For each supplier, write one concise risk note (≤12 words)."
)

# 3) Generate text using Gemma 2B
response = requests.post(
    f"{OLLAMA_URL}/api/generate",
    json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
    timeout=120  # increase timeout for first run
)

# 4) Print the response
if response.status_code == 200:
    data = response.json()
    print(response.json()["response"])
else:
    print("Error:", response.status_code, response.text)