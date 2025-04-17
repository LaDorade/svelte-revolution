from ai_session import AISession
from pocketbase import PocketBase
import threading

def get_ai_sessions(pb_client: PocketBase):
    """
    Récupère les sessions utilisant un scénario avec IA.
    """
    try:
        # Récupérer toutes les sessions actives
        sessions = pb_client.collection("Session").get_full_list()

        sessions_avec_ia = []

        for session in sessions:
            id_scenario = session.scenario
            scenario = pb_client.collection("scenario").get_one(id_scenario)
            if scenario.ai == True:
                sessions_avec_ia.append(session)

        return sessions_avec_ia

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions IA : {e}")
        return []

def start_ai_for_session(session, pb_client: PocketBase):
    ai = AISession(session.id, session.title, pb_client)
    threading.Thread(target=ai.start).start()