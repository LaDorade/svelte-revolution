import time, json, os
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
        self.pending_nodes = []

        self.load_state()

    def load_trigger_nodes(self) -> list:
        try:
            table = self.pb.collection("TriggerNodes").get_list().items
            for ligne in table:
                if ligne.scenario == self.scenario_id:
                    print(f"✅ {len(ligne.nodes)} trigger nodes chargés depuis la BDD")
                    return ligne.nodes
            return []
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
                self.process_pending_nodes_batch()
                time.sleep(20)
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
            self.pending_nodes.append({
                "id" : node.id,
                "title" : node.title,
                "text" : node.text,
            })

            self.save_state()

            print(f"🧾 Nouveau nœud détecté et ajouté au batch : {node.title} (ID: {node.id})")

            #self.check_triggers(node.id, node.title, node.text)

        return

    def build_batch(self):
        """
        Construit le batch à envoyer à Mistral à partir des pending_nodes et des triggers disponibles.
        Retourne un dictionnaire prêt à être sérialisé en JSON.
        Affiche les available_triggers à la fin.
        """
        batch = {}
        all_available_triggers = []
        for pending_node in self.pending_nodes:
            # On ne prend que les triggers activables maintenant
            available_triggers = {}
            for trigger_node in self.trigger_nodes:
                if trigger_node["id"] in self.triggered_nodes:
                    continue
                if "conditions" not in trigger_node or "first" in trigger_node["conditions"]:
                    available_triggers[trigger_node["id"]] = trigger_node["triggers"]

                if "conditions" in trigger_node:
                    for condition in trigger_node["conditions"]:
                        if condition in self.triggered_nodes:
                            available_triggers[trigger_node["id"]] = trigger_node["triggers"]

            batch[pending_node["id"]] = {
                "title": pending_node["title"],
                "text": pending_node["text"],
                "available_triggers": available_triggers
            }
            if available_triggers:
                all_available_triggers.extend(list(available_triggers.values()))

        if all_available_triggers:
            print("Triggers possibles:", all_available_triggers)
        return batch

    def process_pending_nodes_batch(self):
        if not self.pending_nodes:
            return

        print(f"🧾 Traitement du batch en cours... (n={len(self.pending_nodes)})")

        batch = self.build_batch()

        with open("mistral_batch_prompt.txt", "r", encoding="utf-8") as f:
            mistral_prompt = f.read()

        mistral_prompt = mistral_prompt + json.dumps(batch, ensure_ascii=False, indent=4)
        try:
            response = ask_mistral(mistral_prompt)
            response_json = json.loads(response)
            # pour chaque noeud traité du batch
            for node_id in response_json:
                # on regarde la réponse pour chaque trigger
                for trigger in response_json[node_id]:
                    pending_nodes_id = []
                    for pending_node in self.pending_nodes:
                        pending_nodes_id.append(pending_node["id"])
                    # on regarde si le noeud du batch a déclenché un trigger
                    if node_id in pending_nodes_id and "trigger" in trigger and trigger["trigger"] in [True, 'True', 'true']:
                        # on retrouve le trigger_node et on appelle la fonction qui l'ajoute à la session
                        for trigger_node in self.trigger_nodes:
                            if "trigger_id" in trigger and trigger_node["id"] == trigger["trigger_id"]:
                                if trigger_node["id"] not in self.triggered_nodes:
                                    self.trigger_node(node_id, trigger_node)
                                    break
        except Exception as e:
            print(f"❌ Erreur Mistral batch : {e}")

        # on vide le batch
        self.pending_nodes = []
        print(f"🧾 Le batch a été traité. En attente de nouveaux nodes...")

    def trigger_node(self, node_id, trigger_node):
        try:
            print(f"⚡ Trigger détecté parmis: {trigger_node["triggers"]}. Création du noeud...")
            title = trigger_node["title"]
            text = trigger_node["text"]
            author = trigger_node["author"]
            self.add_node(node_id, title, text, author)
            self.triggered_nodes.append(trigger_node["id"])
            self.save_state()

            if "is_final" in trigger_node and trigger_node["is_final"] in [True, "true", "True"]:
                self.handle_final_node()
        except Exception as e:
            print("❌ Erreur fonction trigger_node:", e)

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
        new_nodes = []
        while waited < timeout:
            nodes = self.pb.collection("node").get_full_list(query_params={
                "filter": f"session = '{self.session_id}'"
            })
            new_nodes = [n for n in nodes if n.id not in self.known_node_ids]

            time.sleep(10)
            waited += 10
            print(f"⏳ Attente... {waited}/{timeout} sec")

        user_responses = [(n.title, n.text, n.author) for n in new_nodes if n.side != ""]
        one_node_id = new_nodes[0].id if new_nodes else None

        if not user_responses:
            print("⚠️ Aucune réponse reçue après le nœud final.")
            return

        prompt = self.build_final_prompt(user_responses)
        final_story = ask_mistral(prompt)
        self.add_node(one_node_id, "THE END", final_story, "Narrator")

        try:
            self.pb.collection("Session").update(self.session_id, { "completed": True, })
            print(f"✅ La session {self.session_id} a été mise à jour dans la BDD et est désormais complétée.")
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la session {self.session_id} dans la BDD:", e)

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
