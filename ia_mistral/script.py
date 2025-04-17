import time
from pocketbase import PocketBase
from datetime import datetime, timedelta, timezone

# Liste des sessions IA actives
sesssions_ia_actives = []

def fetch_ai_sessions(pb_client: PocketBase) -> list:
    """
    Récupère les sessions utilisant un scénario avec IA.
    """
    try:
        # Récupérer toutes les sessions actives
        sessions: list = pb_client.collection("Session").get_full_list()

        sessions_avec_ia = []

        for session in sessions:
            scenario = pb_client.collection("scenario").get_one(session.scenario)
            if scenario.ai == True:
                sessions_avec_ia.append(session)

        return sessions_avec_ia

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions IA : {e}")
        return []

def fetch_recent_nodes(client) -> list:
    """Récupère les 10 derniers noeuds mis à jour."""
    return client.collection("Node").get_list(
        page=1,
        per_page=10,
        query_params={'sort': '-updated'}
    ).items

def is_recently_updated(node) -> bool:
    """Vérifie si un noeud a été mis à jour dans les 10 dernières minutes."""
    updated_time = datetime.strptime(str(node.updated), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return updated_time >= datetime.now(timezone.utc) - timedelta(minutes=10)

def check_active_ai_sessions(client):
    """Met à jour la liste des sessions IA actives."""
    global sesssions_ia_actives

    sesssions_ia_actives.clear()

    sessions_ia: list = fetch_ai_sessions(client)
    noeuds_recents: list = fetch_recent_nodes(client)

    # Identifie les sessions actives basées sur les noeuds récents
    sessions_actives_id = [noeud.session for noeud in noeuds_recents if is_recently_updated(noeud)]

    # Ajoute les nouvelles sessions actives
    for session in sessions_ia:
        if session not in sesssions_ia_actives and session.id in sessions_actives_id:
            sesssions_ia_actives.append(session)

    # Affiche les sessions IA actives
    print(f"Sessions IA actives trouvées (nb={len(sesssions_ia_actives)}):")
    for session in sesssions_ia_actives:
        print(f"ID session: {session.id} / Id scénario: {session.scenario}")

def main():
    """Point d'entrée principal du script."""
    client = PocketBase("https://db.babel-revolution.fr")

    while True:
        try:
            check_active_ai_sessions(client)
        except Exception as e:
            print(f"❌ Erreur dans le script : {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()