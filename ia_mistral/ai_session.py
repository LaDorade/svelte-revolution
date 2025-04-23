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
        self.trigger_nodes = self.load_trigger_nodes()

        self.load_state()

    def load_trigger_nodes(self):
        try:
            with open("trigger_nodes.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ {len(data)} triggers nodes chargés depuis trigger_nodes.json")
                return data
        except Exception as e:
            print(f"⚠️ Erreur chargement des trigger nodes : {e}")
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
        print(f"🛑 Instance AISession {self.session_id} arrêtée.")

    def start(self):
        print(f"🤖 Instance AISession lancée pour la session {self.session_id} — Scénario: {self.scenario_id}")
        while self.active:
            try:
                self.check_new_nodes()
                time.sleep(2)
            except Exception as e:
                print(f"❌ Erreur AISession {self.session_id} : {e}")
                time.sleep(5)

    def check_new_nodes(self):
        nodes = self.pb.collection("node").get_full_list(query_params={
            "filter": f"session = '{self.session_id}'"
        })

        for node in nodes:
            if node.id in self.known_node_ids:
                continue
            
            # Ignore les noeuds du narrateur
            if node.author == "Narrator":
                self.known_node_ids.add(node.id)
                continue

            self.known_node_ids.add(node.id)
            self.save_state()
            print(f"🧾 Nouveau nœud détecté : {node.title} (ID: {node.id})")

            self.check_triggers(node.id, node.title, node.text)

    def check_triggers(self, node_id, title: str, text: str):
        lower_title = title.lower()
        lower_text = text.lower()

        for trigger_node in self.trigger_nodes:
            # Vérifie si le noeud a déjà été déclenché
            if trigger_node["id"] in self.triggered_nodes:
                continue

            if "condition" not in trigger_node:
                if "trigger" in trigger_node and self.text_matches_trigger(trigger_node["trigger"], lower_text):
                    self.trigger_node(node_id, trigger_node)
                    break

            else:
                # Si c'est le tout premier trigger, il n'a pas de condition
                if trigger_node["condition"] == "first":
                    if "trigger" in trigger_node and self.text_matches_trigger(trigger_node["trigger"], lower_text):
                        self.trigger_node(node_id, trigger_node)
                        break
                # Vérifie si le noeud a une condition (ex: il faut qu'un autre noeud soit déclenché avant)
                elif trigger_node["condition"] in self.triggered_nodes:
                    # Vérifie si le trigger est présent dans le contenu du noeud
                    if "trigger" in trigger_node and self.text_matches_trigger(trigger_node["trigger"], lower_text):
                        self.trigger_node(node_id, trigger_node)
                        break

            #Laisse à mistral le temps de soufler
            time.sleep(1)

    def text_matches_trigger(self, trigger, text):
        print("Trigger actuel:", trigger)
        print("Contenu du noeud traité:", text)
        prompt = f"""Le message suivant contient-il une référence directe ou indirecte, ou est le synonyme, ou est identique
        au mot ou à l'idée suivante (fais le même raisonnement en traduisant en chinois ou en anglais et vise versa): "{trigger}" ?
        Message : "{text}"

        Réponds simplement par : oui ou non."""
        try:
            response = ask_mistral(prompt).strip().lower()
            print("Réponse de Mistral:", response)
            return "oui" in response
        except Exception as e:
            print(f"⚠️ Erreur Mistral lors du matching de trigger : {e}")
            return False

    def trigger_node(self, node_id, trigger_node):
        print(f"⚡ Trigger détecté: {trigger_node["trigger"]}. Création du noeud...")
        title = trigger_node["title"]
        text = trigger_node["text"]
        author = trigger_node["author"]
        self.add_node(node_id, title, text, author)
        self.triggered_nodes.append(trigger_node["id"])
        self.save_state()

        if trigger_node.get("is_final"):
            self.handle_final_node()

    def add_node(self, node_id, title, text, author):
        node_type = "contribution" if author != "Narrator" else "event"
        self.pb.collection("node").create({
            "title": title,
            "text": text,
            "author": author,
            "type": node_type,
            "session": self.session_id,
            "parent": node_id
        })
        print(f"🤖 Noeud IA posté (ID: {node_id}) : {title} avec auteur '{author}'")

    def handle_final_node(self):
        timeout = 120 # faire un timeout plus long
        waited = 0
        print(f"🔚 Dernier trigger node enclenché. Attente des réponses joueurs... ({timeout} sec)")

        # Récupère les nouveaux noeuds jusqu'à ce que le temps soit écoulé
        while waited < timeout:
            nodes = self.pb.collection("node").get_full_list(query_params={
                "filter": f"session = '{self.session_id}'"
            })
            new_nodes = [n for n in nodes if n.id not in self.known_node_ids]

            time.sleep(10)
            waited += 10
            print(f"⏳ Attente... {waited}/{timeout} sec")

        new_nodes = [n for n in nodes if n.id not in self.known_node_ids]
        user_responses = [(n.title, n.text, n.author) for n in new_nodes if n.side != ""]
        one_node_id = new_nodes[0].id if new_nodes else None

        if not user_responses:
            print("⚠️ Aucune réponse reçue après le nœud final.")
            return

        prompt = self.build_final_prompt(user_responses)
        final_story = ask_mistral(prompt)
        self.add_node(one_node_id, "THE END", final_story, "Narrator")

        ## LOGIQUE POUR FICHIER SESSION
        # ✅ Ajout : mise à jour du fichier JSON unique pour toutes les sessions
        status_file = "sessions_status.json"
        session_status = {
            "session_id": self.session_id,
            "etat": "terminée"
        }

        # Charger les données existantes ou créer une nouvelle liste
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                try:
                    all_statuses = json.load(f)
                except json.JSONDecodeError:
                    all_statuses = []
        else:
            all_statuses = []

        # Met à jour ou ajoute l'entrée de la session actuelle
        updated = False
        for entry in all_statuses:
            if entry["session_id"] == self.session_id:
                entry["etat"] = "terminée"
                updated = True
                break

        if not updated:
            all_statuses.append(session_status)

        # Sauvegarder
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(all_statuses, f, ensure_ascii=False, indent=4)


        self.stop()

    def build_final_prompt(self, responses):
        reponses_joueurs = "\n".join(f"- Titre du message: {title} / Nom du disciple: {author} / Contenu (action/intention/choix): {text}" for title, text, author in responses)

        print(reponses_joueurs)

        return f"""Tu es une IA narratrice qui clôture une session de récit interactif dans l'univers mythologique de Sun Wukong.
        Le scénario raconte comment Wukong et ses disciples (les joueurs) ont traversé plusieurs épreuves pour récupérer
        le Rúyì Jīngū Bàng, le bâton magique, auprès du Roi Dragon dans l'océan de la Mer de l'Est.

        Voici les dernières actions et intentions exprimées par les disciples :
        {reponses_joueurs}

        Ta mission est de rédiger un court paragraphe immersif concluant cette session. Cette conclusion :
            -doit être cohérente avec les choix et intentions des disciples,
            -doit servir de dernier nœud dans la session, et donc apporter une sensation de fermeture au récit.
            -peut avoir une tournure humoristique ou absurde selon les choix des disciples.

        Ne formule pas de questions ouvertes ni d'invitations à poursuivre : cette conclusion marque la fin de l'aventure.
        La réponse doit être en anglais.
        La réponse doit être concise, entre 3 et 5 phrases maximum."""
