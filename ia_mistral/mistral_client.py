import os
import time

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import UserMessage

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def ask_mistral(prompt: str, history: list = [], model: str = "open-mistral-nemo", max_retries: int = 3) -> str:
    """
    Envoie un prompt à l'API Mistral avec retry automatique.
    
    Args:
        prompt: Le texte à envoyer à Mistral
        history: Historique de conversation (non utilisé actuellement)
        model: Modèle Mistral à utiliser
        max_retries: Nombre maximum de tentatives
        
    Returns:
        str: Réponse de Mistral ou chaîne vide en cas d'échec
    """
    # Validation de la clé API
    if not MISTRAL_API_KEY:
        print("❌ Clé API Mistral manquante dans les variables d'environnement")
        return ""
    
    # Validation du prompt
    if not prompt or not prompt.strip():
        print("❌ Prompt vide fourni à Mistral")
        return ""
        
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    for attempt in range(max_retries):
        try:
            if attempt == 0:
                print("🧾 Envoi du batch au client Mistral...", end=" ")
            else:
                print(f"🔄 Tentative {attempt + 1}/{max_retries}...", end=" ")
                
            chat_response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    UserMessage(
                        content=prompt,
                    )
                ],
            )
            print("✅ OK")
            
            # Validation et conversion de la réponse
            response_content = chat_response.choices[0].message.content
            if not response_content:
                print("⚠️ Réponse vide de Mistral")
                return ""
            
            # Assure que c'est une chaîne
            if isinstance(response_content, list):
                # Si c'est une liste de ContentChunk, on extrait le texte
                response_content = "".join(str(chunk) for chunk in response_content)
            elif not isinstance(response_content, str):
                response_content = str(response_content)
                
            return response_content

        except Exception as e:
            print(f"❌ Erreur (tentative {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Backoff exponentiel: 1s, 2s, 4s...
                print(f"⏳ Attente {wait_time}s avant nouvelle tentative...")
                time.sleep(wait_time)
            else:
                print(f"❌ Échec définitif après {max_retries} tentatives")
    
    return ""
    