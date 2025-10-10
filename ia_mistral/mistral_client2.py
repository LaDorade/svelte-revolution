import os
import json
import utils

from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import UserMessage
from pydantic import BaseModel, RootModel
from typing import Dict

class TriggerEvaluation(BaseModel):
    trigger_node_id: str
    should_get_triggered: bool
    justification: str

# Supprime la classe NodeTriggerEvaluations
# Le format est directement: node_id -> Dict[trigger_id, TriggerEvaluation]
class TriggerEvaluationBatch(RootModel):
    root: Dict[str, Dict[str, TriggerEvaluation]]

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

with open("mistral_batch_prompt2.txt", "r", encoding="utf-8") as f:
    INSTRUCTION_CONTEXT = f.read()

def ask_mistral(prompt: str, model="mistral-tiny") -> TriggerEvaluationBatch | None:
    if not MISTRAL_API_KEY:
        print("❌ Clé API Mistral manquante dans les variables d'environnement")
        return None
    if not prompt or not prompt.strip():
        print("❌ Prompt vide fourni à Mistral")
        return None
    client = Mistral(api_key=MISTRAL_API_KEY)
    prompt = INSTRUCTION_CONTEXT + "\n" + prompt
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
            print("⚠️ Réponse vide de Mistral")
            return None
        if isinstance(response_content, list):
            response_content = "".join(str(chunk) for chunk in response_content)
        try:
            evaluation_batch = TriggerEvaluationBatch.model_validate_json(response_content)
            return evaluation_batch
        except Exception as e:
            print(f"❌ Erreur parsing de la réponse Mistral: {e}")
            print(f"Réponse reçue: {response_content[:500]}")  # Debug
            return None
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à l'API Mistral: {e}")
        return None
    
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
    
    if result:
        print(result.model_dump_json(indent=2, exclude_unset=True))
        # Accès aux données
        for node_id, triggers in result.root.items():
            print(f"\nNode: {node_id}")
            for trigger_id, evaluation in triggers.items():
                print(f"  {trigger_id}: {evaluation.should_get_triggered} - {evaluation.justification}")
    else:
        print("Aucune réponse valide.")