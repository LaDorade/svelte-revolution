import os
from dotenv import load_dotenv
from pocketbase import PocketBase
import time

load_dotenv()

PB_URL = "https://db.babel-revolution.fr"
PB_EMAIL = os.getenv("POCKETBASE_EMAIL")
PB_PASSWORD = os.getenv("POCKETBASE_PASSWORD")
CHECK_INTERVAL = 3

client = PocketBase(PB_URL)

while True:
    try:
        # Authentification
        admin_data = client.admins.auth_with_password(PB_EMAIL, PB_PASSWORD)
        assert admin_data.is_valid
        print("✅ Authentifié avec succès")

        # Récupération des sessions
        sessions = client.collection("Session").get_full_list()
        print(f"📦 {len(sessions)} session(s) trouvée(s):")

        target_session = None
        for s in sessions:
            scenario_id = s.scenario
            scenario = client.collection("scenario").get_one(scenario_id)
            print(f"• Session ID: {s.id}, Name: {s.name} — Scénario: {scenario.title}")

            if s.name == "Essai_TX":
                target_session = s
                print(f"🎯 Session cible trouvée : {target_session.id}")

        if target_session:
            # Récupération de tous les nodes
            nodes = client.collection("Node").get_full_list()
            print(f"🧩 {len(nodes)} node(s) trouvés")

            for node in nodes:
                if node.session == target_session.id and node.title == "SI28":
                    print(f"🔍 Node à modifier trouvé : {node.id} — Titre: {node.title}")

                    #Mise à jour du node
                    updated_node = client.collection("Node").update(node.id, {
                        "title": "SI28_modifié"  # ou autre champ
                    })
                    print(f"✅ Node modifié : {updated_node.id} — Nouveau titre: {updated_node.title}")
                    break
            else:
                print("❌ Aucun node avec le titre 'SI28' lié à cette session.")
        else:
            print("❌ Aucune session nommée 'Essai_TX' trouvée.")

        break

    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("⏳ Nouvelle tentative dans 5 secondes...")
        time.sleep(5)
