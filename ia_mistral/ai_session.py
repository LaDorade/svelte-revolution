import utils
import json
import time
import os

from pocketbase.models.record import Record
from pocketbase import PocketBase

from ia_mistral.mistral_client import ask_mistral, TriggerEvaluationBatch, FINAL_PROMPT_CONTEXT_FILE

SESSION_DATA_FOLDER = "sessions_data"

class AISession:
    def __init__(self, session: Record, pb_client: PocketBase):
        self.session = session
        self.pb_client = pb_client

        self.session_id = session.id
        self.session_name = getattr(session, 'name', None)
        self.scenario_id = getattr(session, 'scenario', None)

        self.log_file_name = utils.get_log_file_name(prefix="ai_session2")
        self.session_file = os.path.join(SESSION_DATA_FOLDER, f"session_{session.id}.json")
        self.triggered_nodes_file = os.path.join(SESSION_DATA_FOLDER, f"triggered_nodes_{session.id}.json")

        self.trigger_nodes: list[dict] = []  # liste des trigger nodes du scénario
        self.triggered_nodes: list[str] = []  # trigger nodes de la session déjà déclenchés [id1, id2, ...]
        self.available_trigger_nodes: list[tuple[str, list[str]]] = []  # (trigger_id, [triggers])
        self.processed_nodes: dict[str, dict] = {}  # nodes de la session déjà traités
        self.pending_batch: list[dict] = []  # nodes en attente d'évaluation par l'IA

        self.active = False

        utils.log_message(f"[AISession '{self.session_name}'] Initialisation terminée", self.log_file_name)

    def start(self):
        if not self.session_id or not self.session_name or not self.scenario_id:
            utils.log_message(f"Session {self.session.id} invalide, impossible de démarrer AISession.", self.log_file_name)
            return
        self.trigger_nodes = self.get_trigger_nodes()
        self.triggered_nodes = self.get_already_triggered_nodes()
        self.available_trigger_nodes = self.get_available_trigger_nodes()
        self.processed_nodes = self.get_already_processed_nodes()
        self.active = True
        utils.log_message(f"[AISession '{self.session_name}'] Démarrage réussi", self.log_file_name)
        self.start_processing_loop()

    def stop(self):
        self.save_processed_nodes()
        self.active = False
        utils.log_message(f"[AISession '{self.session_name}'] Arrêt de l'instance IA", self.log_file_name)

    def get_trigger_nodes(self) -> list[dict]:
        try:
            # Filtre directement par scenario
            trigger_nodes_records = self.pb_client.collection("TriggerNodes").get_list(
                query_params={'filter': f'scenario="{self.scenario_id}"', 'perPage': 1}
            )
            
            if not trigger_nodes_records.items:
                utils.log_message(f"Aucun TriggerNodes trouvé pour le scénario {self.scenario_id}.", self.log_file_name)
                return []
            
            # Prend le premier Record trouvé
            trigger_nodes_record = trigger_nodes_records.items[0]
            trigger_nodes = getattr(trigger_nodes_record, 'nodes', None)
            
            if not isinstance(trigger_nodes, list):
                utils.log_message(f"Le champ 'nodes' dans TriggerNodes pour le scénario {self.scenario_id} n'est pas une liste.", self.log_file_name)
                return []

            utils.log_message(f"[AISession '{self.session_name}'] {len(trigger_nodes)} trigger nodes chargés", self.log_file_name)
            return trigger_nodes
            
        except Exception as e:
            utils.log_message(f"Erreur lors de la récupération des TriggerNodes pour le scénario {self.scenario_id}: {e}", self.log_file_name)
            return []
        
    def get_already_triggered_nodes(self) -> list[str]:
        if not os.path.exists(SESSION_DATA_FOLDER):
            os.makedirs(SESSION_DATA_FOLDER)
        if not os.path.exists(self.triggered_nodes_file):
            with open(self.triggered_nodes_file, "w") as f:
                f.write("[]")
            return []
        with open(self.triggered_nodes_file, "r") as f:
            content = f.readline()
            return content.strip("[]").replace('"', '').split(",") if content.strip("[]") else []
        
    def get_available_trigger_nodes(self) -> list[tuple[str, list[str]]]:
        available_triggers = []
        for trigger_node in self.trigger_nodes:
            trigger_id = trigger_node.get("id")
            # Vérifie si le trigger_id est valide et non déjà déclenché
            if not trigger_id or trigger_id in self.triggered_nodes:
                continue
            triggers = trigger_node.get("triggers", [])
            conditions = trigger_node.get("conditions", [])
            # Si pas de conditions ou "first" dans conditions
            if not conditions or "first" in conditions:
                available_triggers.append((trigger_id, triggers))
                continue
            # Si toutes les conditions sont respectées
            for condition in conditions:
                if condition not in self.triggered_nodes:
                    break
            else:
                available_triggers.append((trigger_id, triggers))
        return available_triggers
    
    def update_available_trigger_nodes(self) -> None:
        self.available_trigger_nodes = self.get_available_trigger_nodes()
        utils.log_message(f"[AISession '{self.session_name}'] Triggers disponibles mis à jour: {list(self.available_trigger_nodes)}", self.log_file_name)
        
    def get_already_processed_nodes(self) -> dict[str, dict]:
        # Crée le dossier s'il n'existe pas
        if not os.path.exists(SESSION_DATA_FOLDER):
            os.makedirs(SESSION_DATA_FOLDER)
        # Crée le fichier s'il n'existe pas
        if not os.path.exists(self.session_file):
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        # Lit le fichier JSON
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                processed_nodes = json.load(f)
            utils.log_message(f"[AISession '{self.session_name}'] {len(processed_nodes)} nodes déjà traités chargés depuis {self.session_file}", self.log_file_name)
            return processed_nodes
        except json.JSONDecodeError as e:
            utils.log_message(f"[AISession '{self.session_name}'] Erreur lors de la lecture du fichier JSON: {e}", self.log_file_name)
            return {}
    
    def save_processed_nodes(self) -> None:
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.processed_nodes, f, ensure_ascii=False, indent=2)
        utils.log_message(f"[AISession '{self.session_name}'] État sauvegardé dans {self.session_file}", self.log_file_name)

    def start_processing_loop(self):
        utils.log_message(f"[AISession '{self.session_name}'] Lancement de la boucle de traitement", self.log_file_name)
        while self.active:
            try:
                new_nodes: list[dict] = self.fetch_new_nodes()
                if new_nodes:
                    utils.log_message(f"[AISession '{self.session_name}'] {len(new_nodes)} nouveaux nodes détectés", self.log_file_name)
                    self.pending_batch.extend(new_nodes)
                
                if self.pending_batch:
                    utils.log_message(f"[AISession '{self.session_name}'] Traitement d'un batch de {len(self.pending_batch)} nodes", self.log_file_name)
                    self.process_pending_batch()
                
                time.sleep(5)  # Pause avant la prochaine itération
            except Exception as e:
                utils.log_message(f"[AISession '{self.session_name}'] Erreur dans la boucle de traitement: {e}", self.log_file_name)
                time.sleep(10)  # Pause plus longue en cas d'erreur
        utils.log_message(f"[AISession '{self.session_name}'] Boucle de traitement arrêtée", self.log_file_name)

    def fetch_new_nodes(self) -> list[dict]:
        try:
            nodes_records = self.pb_client.collection("Node").get_list(
                query_params={'filter': f'session="{self.session_id}"', 'perPage': 50}
            )
            new_nodes = []
            for record in nodes_records.items:
                node_id = getattr(record, 'id', None)
                if node_id and node_id not in self.processed_nodes:
                    if getattr(record, 'type') == "contribution" and getattr(record, 'author') != "Narrator":
                        node_data = {
                            "id": node_id,
                            "title": getattr(record, 'title', ''),
                            "text": getattr(record, 'text', ''),
                            "author": getattr(record, 'author', ''),
                            "parent": getattr(record, 'parent', ''),
                            "side": getattr(record, 'side', ''),
                        }
                        new_nodes.append(node_data)
            return new_nodes
        except Exception as e:
            utils.log_message(f"[AISession '{self.session_name}'] Erreur lors de la récupération des nouveaux nodes: {e}", self.log_file_name)
            return []
        
    def process_pending_batch(self):
        if not self.pending_batch:
            return
        # Prépare le prompt pour Mistral au format JSON attendu
        nodes_dict = {}
        for node in self.pending_batch:
            node_id = node["id"]
            title = node.get("title", "")
            text = node.get("text", "")
            # Récupère les triggers disponibles pour ce node
            available_triggers = {}
            for trigger_id, trigger_contents in self.available_trigger_nodes:
                available_triggers[trigger_id] = trigger_contents
            nodes_dict[node_id] = {
                "title": title,
                "text": text,
                "available_triggers": available_triggers
            }
        utils.log_message(f"[AISession '{self.session_name}'] Triggers disponibles pour le batch: {list(self.available_trigger_nodes)}", self.log_file_name)
        prompt = json.dumps(nodes_dict, ensure_ascii=False, indent=2)
        result = ask_mistral(prompt)
        if result is None:
            utils.log_message(f"[AISession '{self.session_name}'] Échec de l'appel à Mistral, le batch sera réessayé plus tard", self.log_file_name)
            return  # Ne vide pas le batch, réessaiera plus tard
        elif not isinstance(result, TriggerEvaluationBatch):
            utils.log_message(f"[AISession '{self.session_name}'] Échec de l'appel à Mistral, mauvais format de réponse reçu", self.log_file_name)
            return
        
        # Ajoute les nodes du batch à processed_nodes avant de traiter les evaluations
        for node in self.pending_batch:
            node_id = node["id"]
            if node_id not in self.processed_nodes:
                self.processed_nodes[node_id] = node
        
        # Traite la réponse
        for node_id, triggers in result.root.items():
            for trigger_id, evaluation in triggers.items():
                if evaluation.should_get_triggered and trigger_id not in self.triggered_nodes:
                    utils.log_message(f"[AISession '{self.session_name}'] Déclenchement du trigger {trigger_id} par le node {node_id}. "
                                      f"Justification: {evaluation.justification}", self.log_file_name)
                    self.trigger_node(trigger_id, node_id)
                    self.triggered_nodes.append(trigger_id)
                    self.save_triggered_nodes()

        # Met à jour les triggers disponibles après traitement du batch
        self.update_available_trigger_nodes()
        
        # Sauvegarde l'état de la session
        self.save_processed_nodes()
        
        # Vide le batch
        self.pending_batch = []
        utils.log_message(f"[AISession '{self.session_name}'] Batch traité et sauvegardé", self.log_file_name)

    def trigger_node(self, trigger_id: str, parent_node_id: str) -> None:
        trigger_node = next((node for node in self.trigger_nodes if node.get("id") == trigger_id), None)
        if not trigger_node:
            utils.log_message(f"[AISession '{self.session_name}'] Trigger node {trigger_id} non trouvé, probablement une erreur dans la réponse de Mistral", self.log_file_name)
            return
        try:
            new_node_data = {
                "title": trigger_node.get("title", ""),
                "text": trigger_node.get("text", ""),
                "author": trigger_node.get("author", ""),
                "session": self.session_id,
                "parent": parent_node_id,
                "type": "event"
            }
            new_record = self.pb_client.collection("Node").create(new_node_data)
            utils.log_message(f"[AISession '{self.session_name}'] Trigger node {trigger_id} inséré avec succès (ID: {new_record.id})", self.log_file_name)
            if trigger_node.get("is_final", False):
                self.handle_final_node()
        except Exception as e:
            utils.log_message(f"[AISession '{self.session_name}'] Erreur lors du déclenchement du trigger node {trigger_id}: {e}", self.log_file_name)

    def save_triggered_nodes(self) -> None:
        triggered_nodes_str = json.dumps(self.triggered_nodes, ensure_ascii=False)
        with open(self.triggered_nodes_file, "w", encoding="utf-8") as f:
            f.write(triggered_nodes_str)
        utils.log_message(f"[AISession '{self.session_name}'] Triggered nodes sauvegardés dans {self.triggered_nodes_file}", self.log_file_name)

    def handle_final_node(self) -> None:
        # Collecte les nouveaux nodes pendant wait_time secondes
        new_nodes: list[dict] = []
        k = 30
        wait_time = 2 * k
        iterations = 0
        max_iterations = wait_time // k

        utils.log_message(f"[AISession '{self.session_name}'] Déclenchement du node final, collecte des derniers messages pendant {wait_time} secondes...", self.log_file_name)
        
        while iterations < max_iterations:
            time.sleep(k)
            fetched = self.fetch_new_nodes()
            if fetched:
                new_nodes.extend(fetched)
                utils.log_message(f"[AISession '{self.session_name}'] {len(fetched)} nouveaux messages collectés (total: {len(new_nodes)})", self.log_file_name)
            iterations += 1

        # Ajoute les nouveaux nœuds à processed_nodes
        for node in new_nodes:
            self.processed_nodes[node["id"]] = node
        self.save_processed_nodes()

        # Gère le cas où aucun nouveau nœud n'a été collecté
        if not new_nodes:
            utils.log_message(f"[AISession '{self.session_name}'] Aucun nouveau message collecté pour la conclusion", self.log_file_name)
            final_node_message = "The adventure comes to an end. The disciples have completed their quest."
        else:
            # Construit le prompt au format JSON pour plus de clarté
            nodes_for_prompt = []
            for node in new_nodes:
                nodes_for_prompt.append({
                    "author": node.get("author", "Unknown"),
                    "title": node.get("title", ""),
                    "text": node.get("text", ""),
                    "side": node.get("side", "")
                })
            
            prompt = json.dumps(nodes_for_prompt, ensure_ascii=False, indent=2)
            utils.log_message(f"[AISession '{self.session_name}'] Envoi de {len(new_nodes)} messages à Mistral pour génération de la conclusion", self.log_file_name)
            
            final_node_message = ask_mistral(prompt, context_file=FINAL_PROMPT_CONTEXT_FILE)

            if not isinstance(final_node_message, str) or not final_node_message.strip():
                utils.log_message(f"[AISession '{self.session_name}'] Erreur: réponse invalide de Mistral, utilisation d'une conclusion par défaut", self.log_file_name)
                final_node_message = "The disciples complete their journey, each carrying the lessons learned along the way."
        
        # Détermine le parent du node final
        # Utilise le dernier node collecté, ou sinon cherche le dernier node event créé
        parent_id = ""
        if new_nodes:
            parent_id = new_nodes[-1].get("id", "")
        else:
            # Cherche le dernier node event créé (probablement le trigger final)
            try:
                last_events = self.pb_client.collection("Node").get_list(
                    query_params={
                        'filter': f'session="{self.session_id}" && type="event"',
                        'sort': '-created',
                        'perPage': 1
                    }
                )
                if last_events.items:
                    parent_id = last_events.items[0].id
            except Exception as e:
                utils.log_message(f"[AISession '{self.session_name}'] Erreur lors de la recherche du parent: {e}", self.log_file_name)
        
        # Crée le nœud final
        final_node_data = {
            "title": "The End",
            "text": final_node_message,
            "author": "Narrator",
            "session": self.session_id,
            "parent": parent_id,
            "type": "event"
        }

        try:
            created_node = self.pb_client.collection("Node").create(final_node_data)
            utils.log_message(f"[AISession '{self.session_name}'] Node final créé avec succès (ID: {created_node.id})", self.log_file_name)
            self.pb_client.collection("Session").update(self.session_id, { "completed": True, })
            utils.log_message(f"[AISession '{self.session_name}'] Session marquée comme complétée", self.log_file_name)
        except Exception as e:
            utils.log_message(f"[AISession '{self.session_name}'] Erreur lors de la création du node final ou de la mise à jour du statut de la session: {e}", self.log_file_name)

        utils.log_message(f"[AISession '{self.session_name}'] Session terminée", self.log_file_name)
        self.stop()
