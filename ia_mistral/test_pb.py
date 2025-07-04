from pocketbase import PocketBase
import os
from dotenv import load_dotenv

"""
Structure d'un TriggerNode dans la BDD:
id: int
scenario: int
infos: json
{
  "id":
  "conditions": [],
  "triggers": [],
  "title":
  "text":
  "author":
}
created: date
updated: date
"""

if __name__ == "__main__":
    try:
        load_dotenv()
        PB_LOGIN = os.getenv("PB_LOGIN")
        PB_PASSWORD = os.getenv("PB_PASSWORD")
    except Exception as e:
        print("❌ Erreur chargement .env:", e)

    try:
        client = PocketBase("https://db.babel-revolution.fr")
        client.admins.auth_with_password(str(PB_LOGIN), str(PB_PASSWORD))
        # table = client.collection("Session").update("h95i580pr0eeowi", { "completed": False, })
        for i in range(10):
            titre = i
            message = f"ceci est le noeud numero {i}"
            client.collection("Node").create(
                {
                    "title": titre,
                    "text": message,
                    "author": "Bot",
                    "type": "contribution",
                    "session": "h95i580pr0eeowi",
                    "parent": "8k8m58066q4h6ek",
                    "side": "k307wt00z8j5onj",
                }
            )
    except Exception as e:
        print("❌ Erreur Pocketbase:", e)