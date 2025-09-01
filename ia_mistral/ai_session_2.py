import time, json, os
from mistral_client import ask_mistral

DATA_FOLDER = "session_data"


class AISession2:
    def __init__(self, session_id, scenario_id, pb_client):
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.pb = pb_client
        self.active = True
        self.session_file = os.path.join(DATA_FOLDER, f"{session_id}.json")

        # Mémorisation des nœuds déjà connus
        self.known_node_ids = set()

        # Stockage scénario
        self.context = None
        self.coded_sentence = None
        self.hints_number = 3
        self.hints = []
        self.current_hint_index = 0
        self.max_hints = 0
        self.hint_interval = 30  # secondes entre indices

        self.load_state()

    # Sauvegarde / chargement de l'état
    def load_state(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                self.known_node_ids = set(data.get("known_node_ids", []))

    def save_state(self):
        with open(self.session_file, 'w') as f:
            json.dump({
                "known_node_ids": list(self.known_node_ids),
            }, f)

    def stop(self):
        self.active = False
        print(f"🛑 Instance AISession {self.session_id} arrêtée.")

    def start(self):
        print(f"🤖 AISession démarrée pour la session {self.session_id} — scénario 'Project : T1M3'")

        # Récupération du noeud prologue 'Le voyage'
        context_nodes = self.pb.collection("node").get_full_list(query_params={
            "filter": f"session = '{self.session_id}' && author = 'L\\'IA' && title ~ 'Le voyage'"
        })
        if context_nodes:
            self.initial_context_node_id = context_nodes[0].id
            print(f"📌 Nœud contexte initial trouvé : {self.initial_context_node_id}")
        else:
            self.initial_context_node_id = None
            print("⚠️ Aucun nœud contexte initial trouvé.")


        # Attente 2 minutes pour que les joueurs se présentent
        wait_time = 120
        print(f"⏳ Attente de {wait_time} sec pour collecte des présentations joueurs...")
        time.sleep(wait_time)

        self.collect_player_presentations()

    def collect_player_presentations(self):
        nodes = self.pb.collection("node").get_full_list(query_params={
            "filter": f"session = '{self.session_id}'"
        })
        player_nodes = [
            n for n in nodes
            if n.author != "L'IA" and n.id not in self.known_node_ids
        ]

        if not player_nodes:
            print("⚠️ Aucun joueur n'a envoyé de présentation.")
            self.stop()
            return

        print(f"📥 {len(player_nodes)} présentations trouvées.")
        self.generate_historical_context(player_nodes)

    def generate_historical_context(self, player_inputs):
        entries = "\n".join(f"- {n.author}: {n.text}" for n in player_inputs)

        prompt = f"""Tu es une IA de narration immersive.
À partir des idées suivantes des joueurs, crée :
1. Un contexte historique fictif immersif dans l’Histoire du monde (avec lieux, époque, ambiance).
2. Une phrase/mot codée en lien avec ce contexte (cryptée, mystérieuse) que les joueurs doivent deviner. 
   Une sorte d'énigme la réponse peut etre une phrase ou un mot de toute manière la résolution sera 
   l'équipe qui sera le plus proche du mot/phrase que tu auras inventé...
3. Des incides aux nombres de {self.hints_number} indices de plus en plus clairs. Ils doivent aider les joueurs sans leur donner des réponses. 
La tout doit être réalisé en français.

Idées des joueurs:
{entries}

Réponds en JSON avec les clés : context, coded_sentence, hints (liste de {self.hints_number} éléments)."""

        response = ask_mistral(prompt)
        try:
            data = json.loads(response)
            self.context = data["context"]
            self.coded_sentence = data["coded_sentence"]
            self.hints = data["hints"]
            print(f"coded_sentence : {self.coded_sentence}")
            print(f"hints : {self.hints}")
            print("📜 Contexte historique généré avec succès !")
            self.post_context_and_code()
        except Exception as e:
            print("❌ Erreur parsing JSON IA:", e)

    def post_context_and_code(self):
        # Le contexte historique est enfant du contexte initial (si trouvé)
        parent_id = getattr(self, "initial_context_node_id", None)
        context_node_id = self.add_node(parent_id, "Situation Historique", self.context, "L'IA")

        # La phrase mystérieuse est enfant du contexte historique
        phrase_node_id = self.add_node(context_node_id, "La Phrase mystérieuse", "*$I_Z*é Vous devez vous rapprocher de la phrase de l'IA en vous basant sur le contexte (ça peut être n'importe quoi, cherchez bien) *$I_Z*é", "L'IA")

        #On attend le temps d'un indice avant de lancer le premier
        time.sleep(self.hint_interval)

        self.start_hint_loop(phrase_node_id)

    def start_hint_loop(self, parent_node_id):
        self.current_hint_index = 0
        self.max_hints = len(self.hints)
        current_parent_id = parent_node_id

        while self.current_hint_index < self.max_hints and self.active:
            hint_text = self.hints[self.current_hint_index]
            current_parent_id = self.add_node(current_parent_id, f"Indice #{self.current_hint_index + 1}", hint_text,"L'IA")
            self.current_hint_index += 1
            time.sleep(self.hint_interval)

        self.handle_end_of_game()

## AJOUTER LE FAIT DE CENSURER DES MOTS, DEMANDER A MISTRAL DES MOTS CENSURABLES.

    def handle_end_of_game(self):
        print("🔚 Tous les indices ont été envoyés. Attente des réponses...")

        timeout = 90
        waited = 0
        final_answers = []
        while waited < timeout:
            nodes = self.pb.collection("node").get_full_list(query_params={
                "filter": f"session = '{self.session_id}'"
            })

            new_nodes = [
                n for n in nodes
                if n.id not in self.known_node_ids and n.author != "L'IA"
            ]
            final_answers.extend(new_nodes)

            if final_answers:
                break
            time.sleep(10)
            waited += 10

        if not final_answers:
            self.add_node(None, "THE END", "Aucune équipe n'a réussi, L'IA va prendre le contrôle et faire à sa guise", "L'IA")
        else:
            self.evaluate_final_answers(final_answers)

    def evaluate_final_answers(self, answers):
        answer_texts = "\n".join(f"- {n.author}, {n.side}: {n.text}" for n in answers)

        prompt = f"""Voici la phrase codée : {self.coded_sentence}
Voici les indices donnés : {self.hints}
Voici les tentatives de décryptage :
{answer_texts}

Quelle équipe a le mieux décrypté le message, les activites ou les rocops ? Donne une courte conclusion.
Réponds en français, sans dépasser 4 phrases."""

        conclusion = ask_mistral(prompt)
        self.add_node(answers[0].id, "LA FIN", f"La phrase était : {self.coded_sentence}" + conclusion, "L'IA")
        self.pb.collection("Session").update(self.session_id, {"completed": True})
        self.stop()

    def add_node(self, parent_id, title, text, author):
        node_type = "contribution" if author != "L'IA" else "event"
        node = self.pb.collection("node").create({
            "title": title,
            "text": text,
            "author": author,
            "type": node_type,
            "session": self.session_id,
            "parent": parent_id
        })
        print(f"🤖 Nœud IA posté : {title} avec auteur '{author}' (parent={parent_id})")
        return node.id  # ✅ On retourne l'ID pour chaîner les enfants