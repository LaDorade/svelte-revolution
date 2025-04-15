import time
import json
import os
from mistral_client import ask_mistral

DATA_FOLDER = "session_data"

class AISession:
    def __init__(self, session_id, scenario_title, pb_client):
        self.session_id = session_id
        self.scenario_title = scenario_title
        self.pb = pb_client
        self.active = True
        self.session_file = os.path.join(DATA_FOLDER, f"{session_id}.json")

        self.known_node_ids = set()
        self.triggered_nodes = []  # IA nodes already posted
        self.trigger_chain = self.load_trigger_chain()

        self.load_state()

    def load_trigger_chain(self):
        try:
            with open("trigger_nodes.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ {len(data)} déclencheurs IA chargés depuis trigger_nodes.json")
                return data
        except Exception as e:
            print(f"⚠️ Impossible de charger les déclencheurs IA : {e}")
            return []

    def load_state(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                self.known_node_ids = set(data.get("known_node_ids", []))
                self.triggered_nodes = data.get("triggered_nodes", [])

    def save_state(self):
        with open(self.session_file, 'w') as f:
            json.dump({
                "known_node_ids": list(self.known_node_ids),
                "triggered_nodes": self.triggered_nodes
            }, f)

    def stop(self):
        self.active = False
        print(f"🛑 Session IA {self.session_id} arrêtée.")

    def start(self):
        print(f"🤖 Démarrage IA pour la session {self.session_id}")
        while self.active:
            try:
                self.check_new_nodes()
                time.sleep(3)
            except Exception as e:
                print(f"❌ Erreur session IA {self.session_id} : {e}")
                time.sleep(5)

    def check_new_nodes(self):
        nodes = self.pb.collection("node").get_full_list(query_params={
            "filter": f"session = '{self.session_id}'"
        })

        for node in nodes:
            if node.id in self.known_node_ids:
                continue

            self.known_node_ids.add(node.id)
            self.save_state()
            print(f"🧾 Nouveau nœud lu : {node.title}")

            self.check_triggers(node.title)

    def check_triggers(self, text):
        lower_text = text.lower()

        for step in self.trigger_chain:
            if step["id"] in self.triggered_nodes:
                continue

            if "trigger" in step and step["trigger"] in lower_text:
                self.trigger_node(step)
                break

            if "condition" in step and step["condition"] in self.triggered_nodes:
                self.trigger_node(step)
                break

    def trigger_node(self, step):
        print(f"⚡ Déclenchement IA: {step['id']}")
        text = step["text"]
        self.add_node(text)
        self.triggered_nodes.append(step["id"])
        self.save_state()

        if step.get("is_final"):
            self.handle_final_node()

    def add_node(self, text):
        self.pb.collection("node").create({
            "session": self.session_id,
            "title": text,
            "from_ai": True
        })
        print(f"🤖 Noeud IA ajouté: {text[:40]}...")

    def handle_final_node(self):
        print("🔚 Dernier nœud déclenché, en attente des réponses...")
        # Attend les réponses utilisateur au dernier nœud
        target_count = 3
        previous_known = len(self.known_node_ids)
        timeout = 30  # secondes max d'attente
        waited = 0

        while waited < timeout:
            nodes = self.pb.collection("node").get_full_list(query_params={
                "filter": f"session = '{self.session_id}'"
            })
            new_nodes = [n for n in nodes if n.id not in self.known_node_ids]

            if len(new_nodes) >= target_count:
                break

            time.sleep(3)
            waited += 3

        # 📖 Collecte des textes
        user_responses = [n.title for n in nodes if n.id not in self.known_node_ids]
        if not user_responses:
            print("⚠️ Pas de réponse utilisateur, aucune histoire générée.")
            return

        prompt = self.build_final_prompt(user_responses)
        final_story = ask_mistral(prompt)
        self.add_node(final_story)
        self.stop()

    def build_final_prompt(self, responses):
        joined = "\n".join(f"- {r}" for r in responses)
        return f"""
Tu es une IA qui clôture une histoire mystérieuse. Voici les dernières réponses des personnages :

{joined}

Rédige une courte conclusion dramatique et poétique qui résume la fin de cette histoire. Pas plus de 4 lignes.
"""
