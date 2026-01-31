from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY missing")

app = FastAPI(title="Book Summary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

class BookRequest(BaseModel):
    title: str
    author: str | None = None
    description: str

@app.post("/generate")
def generate(book: BookRequest):
    prompt = f"""
Livre : {book.title}
Auteur : {book.author or "Inconnu"}

{book.description}
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            },
            timeout=30
        )

        data = response.json()
        # 🔹 Transformer la réponse pour le frontend
        generated_text = ""
        try:
            generated_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return {"error": "❌ Impossible de lire la réponse d'OpenRouter", "details": data}

        return {"title": book.title, "generated_text": generated_text}

    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Impossible de contacter OpenRouter: {e}"}
