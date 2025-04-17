import time
from pocketbase import PocketBase
import requests
from datetime import datetime, timedelta, timezone

# Liste des sessions IA actives
sesssions_ia_actives = []

def fetch_active_sessions():
    """Récupère les sessions IA actives depuis l'API."""
    url = "http://localhost:8000/sessions_ia_actives"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur lors de la requête vers l'API.")
        return []

def fetch_recent_nodes(client):
    """Récupère les 10 derniers noeuds mis à jour."""
    return client.collection("Node").get_list(
        page=1,
        per_page=10,
        query_params={'sort': '-updated'}
    ).items

def is_recently_updated(node):
    """Vérifie si un noeud a été mis à jour dans les 10 dernières minutes."""
    updated_time = datetime.strptime(str(node.updated), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return updated_time >= datetime.now(timezone.utc) - timedelta(minutes=10)

def check_active_ai_sessions(client):
    """Met à jour la liste des sessions IA actives."""
    global sesssions_ia_actives

    sesssions_ia_actives.clear()

    sessions_ia = fetch_active_sessions()
    recent_nodes = fetch_recent_nodes(client)

    # Identifie les sessions actives basées sur les nœuds récents
    active_session_ids = [node.session for node in recent_nodes if is_recently_updated(node)]

    # Ajoute les nouvelles sessions actives
    for session in sessions_ia:
        if session not in sesssions_ia_actives and session["id"] in active_session_ids:
            sesssions_ia_actives.append(session)

    # Affiche les sessions IA actives
    print("Liste des sessions IA actives :")
    for session in sesssions_ia_actives:
        print(f"ID session: {session['id']} / Id scénario: {session['scenario']}")

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