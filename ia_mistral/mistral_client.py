import os
import json
import utils

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import UserMessage
from pydantic import BaseModel, RootModel
from typing import Dict

LOG_FILE_NAME = "mistral_client.log"

class TriggerEvaluation(BaseModel):
    trigger_node_id: str
    should_get_triggered: bool
    justification: str

class TriggerEvaluationBatch(RootModel):
    root: Dict[str, Dict[str, TriggerEvaluation]]

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
BATCH_PROMPT_CONTEXT_FILE = "mistral_batch_prompt.txt"
FINAL_PROMPT_CONTEXT_FILE = "mistral_final_prompt.txt"

def ask_mistral(prompt: str, context_file=BATCH_PROMPT_CONTEXT_FILE):
    if not MISTRAL_API_KEY:
        print("❌ Clé API Mistral manquante dans les variables d'environnement")
        return None
    if not prompt or not prompt.strip():
        print("❌ Prompt vide fourni à Mistral")
        return None
    
    with open(context_file, "r", encoding="utf-8") as f:
        INSTRUCTION_CONTEXT = f.read()

    model="mistral-tiny"
    client = Mistral(api_key=MISTRAL_API_KEY)
    prompt = INSTRUCTION_CONTEXT + "\n" + prompt
    if context_file == BATCH_PROMPT_CONTEXT_FILE:
        try:
            chat_response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    UserMessage(
                        content=prompt,
                    )
                ],
            )
            response_content = chat_response.choices[0].message.content
            if not response_content:
                utils.log_message(f"[Mistral] Réponse vide de Mistral", LOG_FILE_NAME)
                return None
            if isinstance(response_content, list):
                response_content = "".join(str(chunk) for chunk in response_content)
            try:
                evaluation_batch = TriggerEvaluationBatch.model_validate_json(response_content)
                utils.log_message(f"[Mistral] Réponse de Mistral validée avec succès", LOG_FILE_NAME)
                return evaluation_batch
            except Exception as e:
                utils.log_message(f"[Mistral] Erreur de validation du JSON de Mistral: {e}", LOG_FILE_NAME)
                return None
        except Exception as e:
            utils.log_message(f"[Mistral] Erreur lors de l'appel à l'API Mistral: {e}", LOG_FILE_NAME)
            return None
    elif context_file == FINAL_PROMPT_CONTEXT_FILE:
        try:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    UserMessage(
                        content=prompt
                    )
                ],
            )
            response_content = chat_response.choices[0].message.content
            return response_content
        except Exception as e:
            utils.log_message(f"[Mistral] Erreur lors de l'appel à l'API Mistral: {e}", LOG_FILE_NAME)
            return ""
    
# Exemple d'utilisation
if __name__ == "__main__":
    sample_nodes = {
        "node_1": {
            "title": "Comment démarrer le moteur",
            "text": "Pour démarrer, appuyez sur le bouton de démarrage.",
            "available_triggers": {
                "trigger_1": "démarrer le moteur",
                "trigger_2": "faire le petit train"
            }
        },
        "node_2": {
            "title": "Un bon repas",
            "text": "Manger un repas de homard.. Miam",
            "available_triggers": {
                "trigger_3": "cross the ocean",
                "trigger_4": "eat a lobster"
            }
        }
    }

    prompt = json.dumps(sample_nodes, ensure_ascii=False, indent=2)
    result = ask_mistral(prompt)
    
    if result and type(result) == TriggerEvaluationBatch:
        print(result.model_dump_json(indent=2, exclude_unset=True))
        # Accès aux données
        for node_id, triggers in result.root.items():
            print(f"\nNode: {node_id}")
            for trigger_id, evaluation in triggers.items():
                print(f"  {trigger_id}: {evaluation.should_get_triggered} - {evaluation.justification}")
    else:
        print("Aucune réponse valide.")