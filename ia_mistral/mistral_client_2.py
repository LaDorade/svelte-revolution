import os
import utils

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import UserMessage

LOG_FILE_NAME = "mistral_client2.log"

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
HISTORICAL_CONTEXT_PROMPT_FILE = "mistral_historical_context_prompt.txt"
EVALUATE_ANSWERS_PROMPT_FILE = "mistral_evaluate_answers_prompt.txt"

def ask_mistral(prompt: str, context_file=HISTORICAL_CONTEXT_PROMPT_FILE):
    """
    Appelle l'API Mistral avec un prompt et un fichier de contexte.
    
    Args:
        prompt: Le prompt à envoyer à Mistral (données uniquement)
        context_file: Le fichier contenant les instructions de contexte
        
    Returns:
        - Pour HISTORICAL_CONTEXT_PROMPT_FILE: retourne une chaîne JSON
        - Pour EVALUATE_ANSWERS_PROMPT_FILE: retourne du texte brut
        - None ou "" en cas d'erreur
    """
    if not MISTRAL_API_KEY:
        utils.log_message("[Mistral2] Clé API Mistral manquante dans les variables d'environnement", LOG_FILE_NAME)
        return None
    
    if not prompt or not prompt.strip():
        utils.log_message("[Mistral2] Prompt vide fourni à Mistral", LOG_FILE_NAME)
        return None
    
    # Charger le contexte depuis le fichier
    try:
        with open(context_file, "r", encoding="utf-8") as f:
            INSTRUCTION_CONTEXT = f.read()
    except FileNotFoundError:
        utils.log_message(f"[Mistral2] Fichier de contexte introuvable: {context_file}", LOG_FILE_NAME)
        return None
    except Exception as e:
        utils.log_message(f"[Mistral2] Erreur lors de la lecture du fichier de contexte: {e}", LOG_FILE_NAME)
        return None

    model = "mistral-tiny"
    client = Mistral(api_key=MISTRAL_API_KEY)
    full_prompt = INSTRUCTION_CONTEXT + "\n" + prompt
    
    # Pour le contexte historique, on attend une réponse JSON
    if context_file == HISTORICAL_CONTEXT_PROMPT_FILE:
        try:
            chat_response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    UserMessage(
                        content=full_prompt,
                    )
                ],
            )
            response_content = chat_response.choices[0].message.content
            if not response_content:
                utils.log_message("[Mistral2] Réponse vide de Mistral", LOG_FILE_NAME)
                return None
            
            # Gérer le cas où response_content est une liste
            if isinstance(response_content, list):
                response_content = "".join(str(chunk) for chunk in response_content)
            
            utils.log_message("[Mistral2] Contexte historique généré avec succès", LOG_FILE_NAME)
            return response_content
            
        except Exception as e:
            utils.log_message(f"[Mistral2] Erreur lors de l'appel à l'API Mistral: {e}", LOG_FILE_NAME)
            return None
    
    # Pour l'évaluation des réponses, on attend du texte brut
    elif context_file == EVALUATE_ANSWERS_PROMPT_FILE:
        try:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    UserMessage(
                        content=full_prompt
                    )
                ],
            )
            response_content = chat_response.choices[0].message.content
            
            # Gérer le cas où response_content est une liste
            if isinstance(response_content, list):
                response_content = "".join(str(chunk) for chunk in response_content)
            
            utils.log_message("[Mistral2] Évaluation des réponses générée avec succès", LOG_FILE_NAME)
            return response_content if response_content else ""
            
        except Exception as e:
            utils.log_message(f"[Mistral2] Erreur lors de l'appel à l'API Mistral: {e}", LOG_FILE_NAME)
            return ""
    
    else:
        utils.log_message(f"[Mistral2] Fichier de contexte non reconnu: {context_file}", LOG_FILE_NAME)
        return None


# Exemple d'utilisation
if __name__ == "__main__":
    # Test pour le contexte historique
    print("Test 1: Génération de contexte historique")
    test_prompt1 = """Entrées du journal :
- Jour 1: L'équipage a découvert une carte mystérieuse.
- Jour 2: Une tempête approche.
- Jour 3: Nous avons trouvé un trésor!"""
    
    result1 = ask_mistral(test_prompt1, context_file=HISTORICAL_CONTEXT_PROMPT_FILE)
    if result1:
        print(f"Résultat (JSON): {result1}\n")
    else:
        print("Échec du test 1\n")
    
    # Test pour l'évaluation des réponses
    print("Test 2: Évaluation des réponses")
    test_prompt2 = """Phrase codée : LE TRESOR EST CACHE

Indices donnés : ['La première lettre', 'C'est un lieu', 'Sous la mer']

Tentatives de décryptage :
- Jean, activites: Le trésor est sous l'eau
- Marie, rocops: Le trésor est caché dans une grotte"""
    
    result2 = ask_mistral(test_prompt2, context_file=EVALUATE_ANSWERS_PROMPT_FILE)
    if result2:
        print(f"Résultat (texte): {result2}\n")
    else:
        print("Échec du test 2\n")
