import sqlite3, subprocess, requests

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
conn.close()

# 3) Build the prompt
prompt = (
    "For each supplier, write one short risk note (max 12 words).\n"
    + supplier_text + "\n\n"
    "Risk notes:"
)

# 4) Generate text using Gemma 2B
response = requests.post(
    f"{OLLAMA_URL}/api/generate",
    json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
    timeout=120  # increase timeout for first run
)

# 5) Print the response
if response.status_code == 200:
    data = response.json()
    print("Raw model output:", data["response"])
else:
    print("Error:", response.status_code, response.text)