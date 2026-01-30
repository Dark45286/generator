from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

# ====================
# CONFIG
# ====================
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ Clé API OpenRouter manquante dans le .env")

app = FastAPI(title="Book Summary & Review Generator – LLaMA 3.1 8B")

# ====================
# CORS
# ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================
# SERVIR LE FRONTEND
# ====================
# Monte le dossier frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Route principale pour index.html
@app.get("/")
def read_index():
    return FileResponse("../frontend/index.html")

# ====================
# SCHEMA
# ====================
class BookRequest(BaseModel):
    title: str
    author: str | None = None
    description: str

# ====================
# ROUTE /generate
# ====================
@app.post("/generate")
def generate_summary_and_review(book: BookRequest):
    prompt = f"""
Tu es un critique littéraire professionnel.

Livre : {book.title}
Auteur : {book.author if book.author else "Inconnu"}

Description :
{book.description}

1. Résume clairement le contenu (200‑300 mots).
2. Donne un avis critique argumenté.
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
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )

        if response.status_code != 200:
            return {"error": f"Erreur OpenRouter ({response.status_code})", "details": response.text}

        data = response.json()
        generated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not generated_text:
            return {"error": "❌ Aucun texte généré"}

        return {"title": book.title, "generated_text": generated_text}

    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Impossible de contacter OpenRouter: {e}"}
