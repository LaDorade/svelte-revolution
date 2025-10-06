import os
import threading
import time
import gzip
import shutil

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from pocketbase import PocketBase
from ai_session import AISession
from ai_session_2 import AISession2

"""
Ce script permet de maintenir la liste des sessions IA actives.
Il est exécuté en continu et met à jour la liste 'sesssions_ia_actives'.
Cette liste sert ensuite à instancier une 'AISession' pour chaque session active.
"""

# Configuration
SCENARIO_ID_SPECIAL = "kh8661rifw077i8"
SLEEP_TIME = 5
RECENT_MINUTES = 10
MAX_LOG_LINES = 1000

# Variables globales
sessions_ia_actives = []
instances_AISession = []

def log_activity(message, log_dir="logs", log_file="default_log.txt"):
    """Log une activité avec archivage automatique si >MAX_LOG_LINES lignes."""
    os.makedirs(log_dir, exist_ok=True)
    full_path = os.path.join(log_dir, log_file)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # vérifie si le fichier existe et dépasse MAX_LOG_LINES lignes
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        if lines >= MAX_LOG_LINES:
            # archive le fichier
            archive_name = f"{full_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
            with open(full_path, "rb") as f_in, gzip.open(archive_name, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(full_path)
            print(f"📦 Log archivé: {archive_name}")

    # ajoute le log dans le fichier (nouveau ou existant)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def fetch_all_sessions(pb_client: PocketBase) -> list:
    """Récupère toutes les sessions actives depuis PocketBase."""
    try:
        return pb_client.collection("Session").get_full_list()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions : {e}")
        return []


def fetch_ai_sessions(pb_client: PocketBase) -> list:
    """Récupère les sessions utilisant un scénario avec IA."""
    sessions = fetch_all_sessions(pb_client)
    sessions_avec_ia = []

    for session in sessions:
        try:
            scenario = pb_client.collection("scenario").get_one(session.scenario)
            # Accès sécurisé à l'attribut ai avec getattr
            has_ai = getattr(scenario, 'ai', False)
            if scenario and has_ai:
                sessions_avec_ia.append(session)
        except Exception as e:
            print(f"❌ Erreur récupération scénario {session.scenario}: {e}")

    return sessions_avec_ia


def fetch_recent_nodes(client) -> list:
    """Récupère les 10 derniers nœuds mis à jour."""
    try:
        result = client.collection("Node").get_list(
            page=1,
            per_page=10,
            query_params={'sort': '-updated'}
        )
        return result.items if hasattr(result, 'items') else []
    except Exception as e:
        print(f"❌ Erreur récupération nœuds récents: {e}")
        return []


def is_recently_updated(node) -> bool:
    """Vérifie si un nœud a été mis à jour dans les RECENT_MINUTES dernières minutes."""
    try:
        if not hasattr(node, 'updated') or not node.updated:
            return False
            
        updated_time = datetime.strptime(str(node.updated), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return updated_time >= datetime.now(timezone.utc) - timedelta(minutes=RECENT_MINUTES)
    except (ValueError, AttributeError) as e:
        print(f"❌ Erreur vérification mise à jour nœud {getattr(node, 'id', 'unknown')}: {e}")
        return False


def get_active_session_ids(noeuds_recents: list) -> list:
    """Identifie les IDs des sessions actives basées sur les nœuds récents."""
    active_ids = []
    for noeud in noeuds_recents:
        if is_recently_updated(noeud) and hasattr(noeud, 'session') and noeud.session:
            active_ids.append(noeud.session)
    return list(set(active_ids))  # Supprime les doublons


def update_active_ai_sessions(client):
    """
    Met à jour la liste des sessions IA actives en fonction des sessions et des noeuds récents,
    et log les activités dans logs/aisessions_log.txt.
    """
    global sessions_ia_actives

    log_dir = "logs"
    log_file = "aisessions_log.txt"

    sessions_ia = fetch_ai_sessions(client)
    noeuds_recents = fetch_recent_nodes(client)
    sessions_actives_id = get_active_session_ids(noeuds_recents)

    # id des sessions IA actives actuellement en mémoire
    current_active_ids = [session.id for session in sessions_ia_actives]

    # ajoute les nouvelles sessions IA actives
    for session in sessions_ia:
        # Vérification sécurisée de l'état de completion
        is_completed = getattr(session, 'completed', False)
        if (session.id in sessions_actives_id and 
            session.id not in current_active_ids and 
            not is_completed):
            sessions_ia_actives.append(session)
            log_activity(f"Ajout session IA active {session.id} (scénario {session.scenario})", log_dir, log_file)

    # supprime les sessions qui ne sont plus actives
    for session in sessions_ia_actives[:]:
        if session.id not in sessions_actives_id:
            sessions_ia_actives.remove(session)
            log_activity(f"Suppression session IA inactive {session.id} (scénario {session.scenario})", log_dir, log_file)


def update_instances_AISession(pb_client: PocketBase):
    """
    Met à jour la liste des instances AISession en fonction des sessions IA actives,
    et log les activités dans logs/aisessions_log.txt.
    """

    global instances_AISession
    global sessions_ia_actives

    log_dir = "logs"
    log_file = "aisessions_log.txt"

    # créé des instances pour les nouvelles sessions actives
    active_session_ids = [session.id for session in sessions_ia_actives]
    existing_session_ids = [instance.session_id for instance in instances_AISession]

    # ajoute les nouvelles instances
    for session in sessions_ia_actives:
        is_completed = getattr(session, 'completed', False)
        if session.id not in existing_session_ids and not is_completed:

            # Si le scénario correspond au scénario 2 avec Time
            if session.scenario == SCENARIO_ID_SPECIAL:
                ai_instance = AISession2(session.id, session.scenario, pb_client)
                log_activity(f"Ajout instance AISession2 pour session {session.id} (scénario {session.scenario})", log_dir, log_file)
            else:
                ai_instance = AISession(session.id, session.scenario, pb_client)
                log_activity(f"Ajout instance AISession pour session {session.id} (scénario {session.scenario})", log_dir, log_file)

            instances_AISession.append(ai_instance)
            threading.Thread(target=ai_instance.start, daemon=True).start()

    # supprime les instances pour les sessions qui ne sont plus actives
    for instance in instances_AISession[:]:
        if instance.session_id not in active_session_ids:
            try:
                instance.stop()
            except Exception as e:
                print(f"❌ Erreur arrêt instance {instance.session_id}: {e}")
            instances_AISession.remove(instance)
            log_activity(f"Suppression instance AISession pour session {instance.session_id} (inactive)", log_dir, log_file)
            continue
        if not getattr(instance, 'active', True):
            instances_AISession.remove(instance)
            log_activity(f"Suppression instance AISession pour session {instance.session_id} (inactive/stop)", log_dir, log_file)
            continue


def display_active_ai_sessions():
    """Affiche les sessions IA actives."""
    print(f"Sessions IA actives trouvées (nb={len(sessions_ia_actives)}):")
    for session in sessions_ia_actives:
        print(f"ID session: {session.id} / Id scénario: {session.scenario}")


def display_instances_AISession():
    """Affiche les instances AISession actives."""
    print(f"Instances AISession actives trouvées (nb={len(instances_AISession)}):")
    for instance in instances_AISession:
        print(f"ID session: {instance.session_id} / Id scénario: {instance.scenario_id}")


def main_loop(client):
    """Boucle principale pour surveiller les sessions et instances IA actives."""
    compteur: int = 0
    print(f"🚀 Démarrage surveillance IA - intervalle: {SLEEP_TIME}s")
    
    while True:
        try:
            if compteur == 0 or compteur % (SLEEP_TIME * 10) == 0:
                print(f"🧾 Status: {len(sessions_ia_actives)} sessions actives, {len(instances_AISession)} instances")

            update_active_ai_sessions(client)
            update_instances_AISession(client)

        except Exception as e:
            print(f"❌ Erreur boucle principale: {e}")

        time.sleep(SLEEP_TIME)
        compteur += SLEEP_TIME


def main():
    try:
        load_dotenv()
        PB_LOGIN = os.getenv("PB_LOGIN")
        PB_PASSWORD = os.getenv("PB_PASSWORD")
        
        if not PB_LOGIN or not PB_PASSWORD:
            print("❌ Variables d'environnement PB_LOGIN ou PB_PASSWORD manquantes")
            return
            
    except Exception as e:
        print(f"❌ Erreur chargement .env: {e}")
        return
    
    try:
        client = PocketBase("https://db.babel-revolution.fr")
        # important pour pouvoir faire des delete ou update...
        client.admins.auth_with_password(PB_LOGIN, PB_PASSWORD)
        print("✅ Connexion PocketBase réussie")
        main_loop(client)
    except Exception as e:
        print(f"❌ Erreur Pocketbase: {e}")


if __name__ == "__main__":
    main()
