from ai_session import AISession
from pocketbase import PocketBase
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os, json, threading, time

"""
Ce script permet de maintenir la liste des sessions IA actives.
Il est exécuté en continu et met à jour la liste 'sesssions_ia_actives'.
Cette liste sert ensuite à instancier une 'AISession' pour chaque session active.
"""

# Liste des sessions IA actives qui est mise à jour par le script
sesssions_ia_actives = []

# Liste des instances de 'AISession' créées pour chaque session active
instances_AISession = []


def fetch_all_sessions(pb_client: PocketBase) -> list:
    """Récupère toutes les sessions actives depuis PocketBase."""
    try:
        return pb_client.collection("Session").get_full_list()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions : {e}")
        return []


def fetch_scenario(pb_client: PocketBase, scenario_id: str):
    """Récupère un scénario spécifique par son ID."""
    try:
        return pb_client.collection("scenario").get_one(scenario_id)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du scénario : {e}")
        return None


def fetch_ai_sessions(pb_client: PocketBase) -> list:
    """Récupère les sessions utilisant un scénario avec IA."""
    sessions = fetch_all_sessions(pb_client)
    sessions_avec_ia = []

    for session in sessions:
        scenario = fetch_scenario(pb_client, session.scenario)
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

def is_session_terminated(session_id):
    status_file = "sessions_status.json"

    if not os.path.exists(status_file):
        return False  # Le fichier n'existe pas, donc la session n'est pas terminée

    with open(status_file, "r", encoding="utf-8") as f:
        try:
            all_statuses = json.load(f)
        except json.JSONDecodeError:
            return False  # Fichier vide ou corrompu

    for entry in all_statuses:
        if entry.get("session_id") == session_id:
            return entry.get("etat") == "terminée"

    return False  # session_id non trouvé


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
    """Met à jour la liste des sessions IA actives."""
    global sesssions_ia_actives

    sesssions_ia_actives.clear()

    sessions_ia = fetch_ai_sessions(client)
    noeuds_recents = fetch_recent_nodes(client)
    sessions_actives_id = get_active_session_ids(noeuds_recents)

    for session in sessions_ia:
        if session not in sesssions_ia_actives and session.id in sessions_actives_id:
            if not is_session_terminated(session):
                sesssions_ia_actives.append(session)


def start_ai_for_session(session, pb_client: PocketBase):
    """Démarre une instance AISession pour une session donnée."""
    ai = AISession(session.id, session.title, pb_client)
    threading.Thread(target=ai.start).start()


def update_instances_AISession(pb_client: PocketBase):
    """
    Met à jour la liste des instances AISession en fonction des sessions IA actives.
    """
    global instances_AISession
    global sesssions_ia_actives

    # Créé des instances pour les nouvelles sessions actives
    active_session_ids = [session.id for session in sesssions_ia_actives]
    existing_session_ids = [instance.session_id for instance in instances_AISession]

    # BRUTE FORCE SCENARIO WUKONG ; LES AUTRES SCENARIOS SONT IGNORES
    id_scenario_wukong = "5s484p3jw9ndesl"

    # Ajoute les nouvelles instances
    for session in sesssions_ia_actives:
        if session.id not in existing_session_ids and session.scenario == id_scenario_wukong:
            # print(f"✅ Création d'une instance AISession pour la session {session.id}")
            ai_instance = AISession(session.id, session.scenario, pb_client)
            instances_AISession.append(ai_instance)
            threading.Thread(target=ai_instance.start).start()

    # Supprimer les instances pour les sessions qui ne sont plus actives
    for instance in instances_AISession[:]:
        if instance.session_id not in active_session_ids:
            # print(f"🛑 Suppression de l'instance AISession pour la session {instance.session_id}")
            instance.stop()
            instances_AISession.remove(instance)
            continue
        if instance.active == False:
            instances_AISession.remove(instance)
            continue


def display_active_ai_sessions():
    """Affiche les sessions IA actives."""
    print(f"Sessions IA actives trouvées (nb={len(sesssions_ia_actives)}):")
    for session in sesssions_ia_actives:
        print(f"ID session: {session.id} / Id scénario: {session.scenario}")


def display_instances_AISession():
    """Affiche les instances AISession actives."""
    print(f"Instances AISession actives trouvées (nb={len(instances_AISession)}):")
    for instance in instances_AISession:
        print(f"ID session: {instance.session_id} / Id scénario: {instance.scenario_id}")


def main_loop(client):
    """Boucle principale pour surveiller les sessions IA actives."""
    while True:
        try:
            # print("🔄 Vérification des sessions IA actives...")
            update_active_ai_sessions(client)
            print(f"✅ {len(sesssions_ia_actives)} sessions IA actives trouvées.")
            # print("🔄 Vérification des instances AISession...")
            update_instances_AISession(client)
            print(f"✅ {len(instances_AISession)} instances AISession actives trouvées.")
        except Exception as e:
            print(f"❌ Erreur dans le script : {e}")

        time.sleep(10)


def main():
    try:
        load_dotenv()
        PB_LOGIN = os.getenv("PB_LOGIN")
        PB_PASSWORD = os.getenv("PB_PASSWORD")
    except Exception as e:
        print("❌ Erreur chargement .env:", e)
    
    try:
        client = PocketBase("https://db.babel-revolution.fr")
        client.admins.auth_with_password(str(PB_LOGIN), str(PB_PASSWORD))
        main_loop(client)
    except Exception as e:
        print("❌ Erreur Pocketbase:", e)


if __name__ == "__main__":
    main()
