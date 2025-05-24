import os
import time

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import UserMessage

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")  # devrait être https://api.mistral.ai/v1/chat/completions

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

def ask_mistral(prompt: str, history: list = [], model: str = "open-mistral-nemo") -> str:
    """
    Envoie un prompt à l'API Mistral, avec option d'historique (mode chat).
    Renvoie le contenu de la réponse.
    """
    client = Mistral(api_key=MISTRAL_API_KEY)
    try:
        print("Envoi du batch au client Mistral...", end=" ")
        chat_response = client.chat.complete(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                UserMessage(
                    content=prompt,
                )
            ],
        )
        print("OK")
        # print(chat_response.choices[0].message.content)
        return chat_response.choices[0].message.content

    except Exception as e:
        print(f"❌ Erreur venant du client Mistral : {e}")
        return ""
    