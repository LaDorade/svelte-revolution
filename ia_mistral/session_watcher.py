from ai_session import AISession
from pocketbase import PocketBase
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os, threading, time
import os
from datetime import datetime
import gzip
import shutil

"""
Ce script permet de maintenir la liste des sessions IA actives.
Il est exécuté en continu et met à jour la liste 'sesssions_ia_actives'.
Cette liste sert ensuite à instancier une 'AISession' pour chaque session active.
"""

# Liste des sessions IA actives qui est mise à jour par le script
sessions_ia_actives = []

# Liste des instances de 'AISession' créées pour chaque session active
instances_AISession = []


def log_activity(message, log_dir="logs", log_file="default_log.txt"):
    """Log une activité dans le fichier spécifié. Archive si >1000 lignes."""
    os.makedirs(log_dir, exist_ok=True)
    full_path = os.path.join(log_dir, log_file)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # vérifie si le fichier existe et dépasse 1000 lignes
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        if lines >= 1000:
            # archive le fichier
            archive_name = f"{full_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
            with open(full_path, "rb") as f_in, gzip.open(archive_name, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(full_path)

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
        except Exception as e:
            print(f"❌ Erreur PocketBase en récupérant les informations du scénario {session.scenario}:", e)
        if scenario and scenario.ai:
            sessions_avec_ia.append(session)

    return sessions_avec_ia


def fetch_recent_nodes(client) -> list:
    """Récupère les 10 derniers noeuds mis à jour."""
    try:
        return client.collection("Node").get_list(
            page=1,
            per_page=10,
            query_params={'sort': '-updated'}
        ).items
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des noeuds récents : {e}")
        return []


def is_recently_updated(node) -> bool:
    """Vérifie si un noeud a été mis à jour dans les 10 dernières minutes."""
    try:
        updated_time = datetime.strptime(str(node.updated), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return updated_time >= datetime.now(timezone.utc) - timedelta(minutes=10)
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la mise à jour du noeud : {e}")
        return False


def get_active_session_ids(noeuds_recents: list) -> list:
    """Identifie les IDs des sessions actives basées sur les noeuds récents."""
    return [noeud.session for noeud in noeuds_recents if is_recently_updated(noeud)]


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
        if session.id in sessions_actives_id and session.id not in current_active_ids and session.completed in [False, "False", "false"]:
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
        if session.id not in existing_session_ids and session.completed in [False, "false", "False"]:
            ai_instance = AISession(session.id, session.scenario, pb_client)
            instances_AISession.append(ai_instance)
            threading.Thread(target=ai_instance.start).start()
            log_activity(f"Ajout instance AISession pour session {session.id} (scénario {session.scenario})", log_dir, log_file)

    # supprime les instances pour les sessions qui ne sont plus actives
    for instance in instances_AISession[:]:
        if instance.session_id not in active_session_ids:
            instance.stop()
            instances_AISession.remove(instance)
            log_activity(f"Suppression instance AISession pour session {instance.session_id} (inactive)", log_dir, log_file)
            continue
        if instance.active == False:
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
    sleep_time: int = 5
    compteur: int = 0
    while True:
        try:
            if compteur  == 0 or compteur == sleep_time * 10:
                print(f"🧾 Rappel: les sessions et instances IA sont analysées toutes les {sleep_time} secondes.")

            update_active_ai_sessions(client)
            update_instances_AISession(client)

        except Exception as e:
            print(f"❌ Erreur dans le script : {e}")

        time.sleep(sleep_time)
        compteur += sleep_time


def main():
    try:
        load_dotenv()
        PB_LOGIN = os.getenv("PB_LOGIN")
        PB_PASSWORD = os.getenv("PB_PASSWORD")
    except Exception as e:
        print("❌ Erreur chargement .env:", e)
    
    try:
        client = PocketBase("https://db.babel-revolution.fr")
        # important pour pouvoir faire des delete ou update...
        client.admins.auth_with_password(str(PB_LOGIN), str(PB_PASSWORD))
        main_loop(client)
    except Exception as e:
        print("❌ Erreur Pocketbase:", e)


if __name__ == "__main__":
    main()
