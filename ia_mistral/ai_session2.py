import utils

from pocketbase.models.record import Record
from pocketbase import PocketBase

class AISession:
    def __init__(self, session: Record, pb_client: PocketBase):
        self.session = session
        self.pb_client = pb_client

        self.log_file_name = utils.get_log_file_name("ai_session2")

        self.session_id = session.id
        self.session_name = getattr(session, 'name', None)
        self.scenario_id = getattr(session, 'scenario', None)

        self.trigger_nodes = []

        self.active = False

    def load_trigger_nodes(self) -> list[dict]:
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

    def start(self):
        if not self.session_id or not self.session_name or not self.scenario_id:
            utils.log_message(f"Session {self.session.id} invalide, impossible de démarrer AISession.", self.log_file_name)
            return

        utils.log_message(f"[AISession '{self.session_name}'] Démarrage", self.log_file_name)
        self.trigger_nodes = self.load_trigger_nodes()
        self.active = True

        # todo: recup les known nodes de la session (changer la bdd?)

    def stop(self):
        utils.log_message(f"[AISession '{self.session_name}'] Arrêt", self.log_file_name)
        self.active = False