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
        admin_data = client.admins.auth_with_password(str(PB_LOGIN), str(PB_PASSWORD))
        table = client.collection("TriggerNodes").get_list().items
        for ligne in table:
            for trigger_node in ligne.nodes:
                if "conditions" in trigger_node:
                    print(len(trigger_node["conditions"]))
    except Exception as e:
        print("❌ Erreur Pocketbase:", e)