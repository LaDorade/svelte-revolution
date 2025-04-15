import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")  # devrait être https://api.mistral.ai/v1/chat/completions

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

def ask_mistral(prompt: str, history: list = [], model: str = "mistral-tiny") -> str:
    """
    Envoie un prompt à l'API Mistral, avec option d'historique (mode chat).
    """
    messages = history + [{"role": "user", "content": prompt}]

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        res = requests.post(MISTRAL_API_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"❌ Erreur Mistral : {e}")
        return ""


"""
prompt = "Raconte moi l'histoire de sun wukong"
response = ask_mistral(prompt)
print("🧠 Réponse Mistral :", response)
"""