import time
import json
import os
from mistral_client import ask_mistral

DATA_FOLDER = "session_data"

class AISession:
    def __init__(self, session_id, scenario_id, pb_client):
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.pb = pb_client
        self.active = True
        self.session_file = os.path.join(DATA_FOLDER, f"{session_id}.json")

        self.known_node_ids = set()
        self.triggered_nodes = []  # Identifiants des noeuds IA déjà envoyés
        self.trigger_chain = self.load_trigger_chain()

        self.load_state()

    def load_trigger_chain(self):
        try:
            with open("trigger_nodes.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ {len(data)} déclencheurs IA chargés depuis trigger_nodes.json")
                return data
        except Exception as e:
            print(f"⚠️ Erreur chargement des déclencheurs IA : {e}")
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
        print(f"🤖 IA activée pour la session {self.session_id} — Scénario: {self.scenario_id}")
        while self.active:
            try:
                self.check_new_nodes()
                time.sleep(3)
            except Exception as e:
                print(f"❌ Erreur IA session {self.session_id} : {e}")
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
            print(f"🧾 Nouveau nœud : {node.title}")

            self.check_triggers(node.id, node.title, node.text)

    def check_triggers(self, node_id, title, text):
        lower_title = title.lower()
        lower_text = text.lower()

        for trigger_node in self.trigger_chain:
            if trigger_node["id"] in self.triggered_nodes:
                continue

            if "condition" in trigger_node and trigger_node["condition"] in self.triggered_nodes:
                if "trigger" in trigger_node and self.text_matches_trigger(trigger_node["trigger"], lower_text):
                    self.trigger_node(node_id, trigger_node)
                    break
            elif "trigger" in trigger_node and self.text_matches_trigger(trigger_node["trigger"], lower_text):
                self.trigger_node(node_id, trigger_node)
                break

    def text_matches_trigger(self, trigger, text):
        prompt = f"""
    Le message suivant contient-il une référence directe ou indirecte (même par synonyme ou traduction en chinois) au mot ou à l'idée suivante : "{trigger}" ?
    Message : "{text}"

    Réponds simplement par : oui ou non.
    """
        try:
            response = ask_mistral(prompt).strip().lower()
            return "oui" in response
        except Exception as e:
            print(f"⚠️ Erreur Mistral lors du matching de trigger : {e}")
            return False

    def trigger_node(self, node_id, trigger_node):
        print(f"⚡ Déclenchement de l'IA par le trigger: {trigger_node["trigger"]}")
        title = trigger_node["title"]
        text = trigger_node["text"]
        author = trigger_node["author"]
        self.add_node(node_id, title, text, author)
        self.triggered_nodes.append(trigger_node["id"])
        self.save_state()

        if trigger_node.get("is_final"):
            self.handle_final_node()

    def add_node(self, node_id, title, text, author):
        self.pb.collection("node").create({
            "title": title,
            "text": text,
            "author": author,
            "type": "contribution",
            "session": self.session_id,
            "parent": node_id
        })
        print(f"🤖 Noeud IA posté : {title} avec auteur {author}")

    def handle_final_node(self):
        print("🔚 Dernier nœud IA. Attente des réponses joueurs...")
        target_count = 3
        timeout = 30
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

        new_nodes = [n for n in nodes if n.id not in self.known_node_ids]
        user_responses = [n.title for n in new_nodes]
        one_node_id = new_nodes[0].id if new_nodes else None

        if not user_responses:
            print("⚠️ Aucune réponse reçue après le nœud final.")
            return

        prompt = self.build_final_prompt(user_responses)
        final_story = ask_mistral(prompt)
        self.add_node(one_node_id, "END", final_story, "Mistral")
        self.stop()

    def build_final_prompt(self, responses):
        joined = "\n".join(f"- {r}" for r in responses)
        return f"""
Tu es une IA qui clôture une histoire mystérieuse. Voici les dernières réponses des personnages :

{joined}

Rédige une courte conclusion dramatique et poétique qui résume la fin de cette histoire. Pas plus de 4 lignes.
"""
