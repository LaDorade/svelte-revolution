import os
import time
import json
import utils

from ia_mistral.mistral_client_2 import ask_mistral

DATA_FOLDER = "session_data"
HISTORICAL_CONTEXT_PROMPT_FILE = "mistral_historical_context_prompt.txt"
EVALUATE_ANSWERS_PROMPT_FILE = "mistral_evaluate_answers_prompt.txt"


class AISession2:
    def __init__(self, session_id, scenario_id, pb_client):
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.pb = pb_client
        self.active = True
        self.session_file = os.path.join(DATA_FOLDER, f"{session_id}.json")
        self.log_file_name = utils.get_log_file_name(prefix="ai_session_2")

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
        utils.log_message(f"[AISession2 '{self.session_id}'] Instance arrêtée", self.log_file_name)

    def start(self):
        utils.log_message(f"[AISession2 '{self.session_id}'] Démarrage pour le scénario 'Project : T1M3'", self.log_file_name)

        # Récupération du noeud prologue 'Le voyage'
        context_nodes = self.pb.collection("node").get_full_list(query_params={
            "filter": f"session = '{self.session_id}' && author = 'L\\'IA' && title ~ 'Le voyage'"
        })
        if context_nodes:
            self.initial_context_node_id = context_nodes[0].id
            utils.log_message(f"[AISession2 '{self.session_id}'] Nœud contexte initial trouvé : {self.initial_context_node_id}", self.log_file_name)
        else:
            self.initial_context_node_id = None
            utils.log_message(f"[AISession2 '{self.session_id}'] Aucun nœud contexte initial trouvé", self.log_file_name)


        # Attente 2 minutes pour que les joueurs se présentent
        wait_time = 120
        utils.log_message(f"[AISession2 '{self.session_id}'] Attente de {wait_time}s pour collecte des présentations joueurs", self.log_file_name)
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
            utils.log_message(f"[AISession2 '{self.session_id}'] Aucun joueur n'a envoyé de présentation", self.log_file_name)
            self.stop()
            return

        utils.log_message(f"[AISession2 '{self.session_id}'] {len(player_nodes)} présentations trouvées", self.log_file_name)
        self.generate_historical_context(player_nodes)

    def generate_historical_context(self, player_inputs):
        entries = "\n".join(f"- {n.author}: {n.text}" for n in player_inputs)

        prompt = f"""Nombre d'indices requis : {self.hints_number}

Idées des joueurs:
{entries}"""

        response = ask_mistral(prompt, context_file=HISTORICAL_CONTEXT_PROMPT_FILE)
        if not response:
            utils.log_message(f"[AISession2 '{self.session_id}'] Réponse vide de Mistral", self.log_file_name)
            return
            
        try:
            data = json.loads(response)
            self.context = data.get("context", "")
            self.coded_sentence = data.get("coded_sentence", "")
            self.hints = data.get("hints", [])
            
            if not self.context or not self.coded_sentence or not self.hints:
                utils.log_message(f"[AISession2 '{self.session_id}'] Données manquantes dans la réponse JSON", self.log_file_name)
                return
                
            utils.log_message(f"[AISession2 '{self.session_id}'] Phrase codée : {self.coded_sentence}", self.log_file_name)
            utils.log_message(f"[AISession2 '{self.session_id}'] Indices : {self.hints}", self.log_file_name)
            utils.log_message(f"[AISession2 '{self.session_id}'] Contexte historique généré avec succès", self.log_file_name)
            self.post_context_and_code()
        except Exception as e:
            utils.log_message(f"[AISession2 '{self.session_id}'] Erreur parsing JSON IA: {e}", self.log_file_name)

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
        utils.log_message(f"[AISession2 '{self.session_id}'] Tous les indices ont été envoyés. Attente des réponses", self.log_file_name)

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

        prompt = f"""Phrase codée : {self.coded_sentence}

Indices donnés : {self.hints}

Tentatives de décryptage :
{answer_texts}"""

        conclusion = ask_mistral(prompt, context_file=EVALUATE_ANSWERS_PROMPT_FILE)
        if not conclusion:
            conclusion = "Les équipes ont fait de leur mieux pour résoudre l'énigme."
            
        final_text = f"La phrase était : {self.coded_sentence}\n\n{conclusion}"
        self.add_node(answers[0].id, "LA FIN", final_text, "L'IA")
        self.pb.collection("Session").update(self.session_id, {"completed": True})
        utils.log_message(f"[AISession2 '{self.session_id}'] Session marquée comme complétée", self.log_file_name)
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
        utils.log_message(f"[AISession2 '{self.session_id}'] Nœud IA posté : {title} avec auteur '{author}' (parent={parent_id})", self.log_file_name)
        return node.id  # ✅ On retourne l'ID pour chaîner les enfants