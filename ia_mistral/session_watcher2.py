import os
import time
import threading
import utils

from pocketbase import PocketBase
from pocketbase.models.record import Record
from pocketbase.services.realtime_service import MessageData
from dotenv import load_dotenv
from datetime import datetime

from ai_session2 import AISession

INACTIVE_TIMEOUT = 600  # secondes avant de considérer une session comme inactive
CHECK_INTERVAL = 30  # secondes entre chaque affichage des sessions actives

LOG_FILE_NAME = f"session_watcher2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

active_ai_sessions: list[tuple[Record, AISession, int, threading.Thread]] = []
# Lock pour protéger l'accès concurrent à la liste
active_ai_sessions_lock = threading.Lock()

def get_session_from_record(record: Record, client: PocketBase) -> Record | None:
    session_id = getattr(record, 'session', None)
    if session_id is None:
        return None

    return client.collection("Session").get_one(session_id)

def session_has_ai_scenario(session: Record, client: PocketBase) -> bool:
    scenario_id = getattr(session, 'scenario', None)
    if scenario_id is None:
        return False

    scenario = client.collection("Scenario").get_one(scenario_id)
    if scenario is None:
        return False

    return getattr(scenario, 'ai', False)

def on_node_change(event: MessageData, client: PocketBase):
    session = get_session_from_record(event.record, client)
    if session is None:
        utils.log_message(f"Aucune session trouvée pour l'événement Node: {event.action}, record id: {getattr(event.record, 'id', None)}", LOG_FILE_NAME)
        return
    if not session_has_ai_scenario(session, client):
        utils.log_message(f"La session ne possède pas de scénario IA: {event.action}, record id: {getattr(event.record, 'id', None)}", LOG_FILE_NAME)
        return
    session_id = getattr(session, 'id', None)
    if session_id is None:
        utils.log_message(f"Aucun ID de session trouvé pour l'événement Node: {event.action}, record id: {getattr(event.record, 'id', None)}", LOG_FILE_NAME)
        return
    session_name = getattr(session, 'name', None)
    if session_name is None:
        utils.log_message(f"Aucun nom de session trouvé pour l'événement Node: {event.action}, record id: {getattr(event.record, 'id', None)}", LOG_FILE_NAME)
        return
    
    utils.log_message(f"Nouvelle session IA active détectée: {session_name} (ID: {session_id})", LOG_FILE_NAME)

    with active_ai_sessions_lock:
        # Vérifie si la session est déjà dans la liste active_ai_sessions
        for i, (sess_record, ai_sess, last_active, thread) in enumerate(active_ai_sessions):
            if getattr(sess_record, 'id', None) == session_id:
                # Met à jour le timestamp de la dernière activité
                active_ai_sessions[i] = (sess_record, ai_sess, int(time.time()), thread)
                utils.log_message(f"Activité détectée pour la session IA déjà active: {session_name} (ID: {session_id})", LOG_FILE_NAME)
                utils.log_message(f"Timestamp de dernière activité mis à jour pour la session: {session_name} (ID: {session_id})", LOG_FILE_NAME)
                return

        # Si la session n'est pas dans la liste, crée une nouvelle instance AISession et lance son thread
        utils.log_message(f"Création de l'instance AISession pour la session: {session_name} (ID: {session_id})", LOG_FILE_NAME)
        ai_session = AISession(session, client)
        thread = threading.Thread(target=ai_session.start, daemon=True)
        utils.log_message(f"Lancement du thread pour l'instance AISession de la session: {session_name} (ID: {session_id})", LOG_FILE_NAME)
        thread.start()
        active_ai_sessions.append((session, ai_session, int(time.time()), thread))

def main():
    load_dotenv()

    PB_LOGIN = os.getenv("PB_LOGIN")
    PB_PASSWORD = os.getenv("PB_PASSWORD")

    if PB_LOGIN is None or PB_PASSWORD is None:
        raise ValueError("PB_LOGIN and PB_PASSWORD environment variables must be set.")

    client = PocketBase("https://db.babel-revolution.fr")
    client.admins.auth_with_password(PB_LOGIN, PB_PASSWORD)

    def handler(event: MessageData):
        on_node_change(event, client)

    client.collection("Node").subscribe(handler)
    utils.log_message("Connexion PocketBase réussie et surveillance des changements de la collection Node", LOG_FILE_NAME)

    timer = 0
    while True:
        if timer >= CHECK_INTERVAL-1:
            timer = 0
            with active_ai_sessions_lock:
                utils.log_message(f"Vérification des sessions IA actives (nb={len(active_ai_sessions)})...", LOG_FILE_NAME)
                for i, (session_record, ai_session, last_active, thread) in enumerate(active_ai_sessions):
                    session_id = getattr(session_record, 'id', None)
                    session_name = getattr(session_record, 'name', 'Unknown')
                    utils.log_message(f" - Session: {session_name} (ID: {session_id}), Dernière activité il y a: {int(time.time()) - last_active}s", LOG_FILE_NAME)
                utils.log_message(f"Note 1: les sessions inactives depuis {INACTIVE_TIMEOUT} secondes seront désactivées automatiquement.", LOG_FILE_NAME)
                utils.log_message(f"Note 2: Ce message est affiché toutes les {CHECK_INTERVAL} secondes.", LOG_FILE_NAME)

        with active_ai_sessions_lock:
            i = 0
            while i < len(active_ai_sessions):
                session_record, ai_session, last_active, thread = active_ai_sessions[i]
                session_id = getattr(session_record, 'id', None)
                if session_id is None:
                    i += 1
                    continue

                try:
                    client.collection("Session").get_one(session_id)
                except Exception:
                    # Si la session n'existe plus, désactive l'instance AISession et la retire de la liste
                    ai_session.stop()
                    active_ai_sessions.pop(i)
                    utils.log_message(f"La session {getattr(session_record, 'name', 'Unknown')} (ID: {session_id}) n'existe plus dans la base de données.", LOG_FILE_NAME)
                    utils.log_message(f"Session supprimée de la liste des sessions actives", LOG_FILE_NAME)
                    continue

                # Si la session est inactive depuis plus de INACTIVE_TIMEOUT secondes, désactive l'instance AISession et la retire de la liste
                if int(time.time()) - last_active > INACTIVE_TIMEOUT:
                    ai_session.stop()
                    utils.log_message(f"Session inactive depuis plus de {INACTIVE_TIMEOUT} secondes: {getattr(session_record, 'name', 'Unknown')} (ID: {session_id})", LOG_FILE_NAME)
                    utils.log_message(f"Désactivation de l'instance AISession pour la session", LOG_FILE_NAME)
                    active_ai_sessions.pop(i)
                    continue

                i += 1

        timer += 1
        time.sleep(1)

if __name__ == "__main__":
    main()