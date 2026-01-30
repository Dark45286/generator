import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

json_data = {
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Bonjour, fais un test."}],
    "temperature": 0.7,
    "max_tokens": 50
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
print("Status code:", response.status_code)
print("Response:", response.text)
