import os
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from pocketbase import PocketBase

load_dotenv()

def get_pocketbase_client():
    """
    Crée et authentifie un client PocketBase.
    
    Returns:
        PocketBase: Client authentifié
        
    Raises:
        Exception: Si la connexion ou l'authentification échoue
    """
    # Validation des variables d'environnement
    email = os.getenv("POCKETBASE_EMAIL")
    password = os.getenv("POCKETBASE_PASSWORD")
    
    if not email or not password:
        raise ValueError("Variables d'environnement POCKETBASE_EMAIL ou POCKETBASE_PASSWORD manquantes")
    
    try:
        pb = PocketBase("https://db.babel-revolution.fr")
        admin_data = pb.admins.auth_with_password(email, password)
        
        if not admin_data:
            raise Exception("Échec de l'authentification PocketBase")
            
        print("✅ Connexion PocketBase réussie")
        return pb
        
    except Exception as e:
        print(f"❌ Erreur connexion PocketBase: {e}")
        raise

def get_target_sessions(client, scenario_id):
    """
    Récupère les sessions pour un scénario donné.
    
    Args:
        client: Client PocketBase authentifié
        scenario_id: ID du scénario à rechercher
        
    Returns:
        List: Sessions correspondantes ou liste vide en cas d'erreur
    """
    if not client:
        print("❌ Client PocketBase non fourni")
        return []
        
    if not scenario_id:
        print("❌ ID de scénario non fourni")
        return []
    
    try:
        all_sessions = client.collection("Session").get_full_list()
        
        if not all_sessions:
            print("⚠️ Aucune session trouvée")
            return []
            
        target_sessions = [s for s in all_sessions if getattr(s, 'scenario', None) == scenario_id]
        print(f"✅ {len(target_sessions)} session(s) trouvée(s) pour le scénario {scenario_id}")
        
        return target_sessions
        
    except Exception as e:
        print(f"❌ Erreur récupération sessions pour scénario {scenario_id}: {e}")
        return []

def get_nodes_for_session(client, session_id):
    """
    Récupère tous les nœuds d'une session (version synchrone).
    
    Args:
        client: Client PocketBase
        session_id: ID de la session
        
    Returns:
        List: Nœuds de la session ou liste vide en cas d'erreur
    """
    if not client:
        print("❌ Client PocketBase non fourni")
        return []
        
    if not session_id:
        print("❌ ID de session non fourni")
        return []
    
    try:
        nodes = client.collection("Node").get_full_list(
            query_params={"filter": f"session = '{session_id}'"}
        )
        
        print(f"✅ {len(nodes)} nœud(s) récupéré(s) pour la session {session_id}")
        return nodes
        
    except Exception as e:
        print(f"❌ Erreur récupération nœuds session {session_id}: {e}")
        return []

def post_node_to_session(client, session_id, text, title="Node IA", author="ia_mistral"):
    """
    Crée un nouveau nœud dans une session (version synchrone).
    
    Args:
        client: Client PocketBase
        session_id: ID de la session
        text: Contenu du nœud
        title: Titre du nœud
        author: Auteur du nœud
        
    Returns:
        str: ID du nœud créé ou None en cas d'erreur
    """
    if not client:
        print("❌ Client PocketBase non fourni")
        return None
        
    if not session_id:
        print("❌ ID de session non fourni")
        return None
        
    if not text or not text.strip():
        print("❌ Contenu du nœud vide")
        return None
    
    try:
        node = client.collection("Node").create({
            "session": session_id,
            "title": title,
            "content": text,
            "author": author,
            "type": "contribution"
        })
        
        print(f"✅ Nœud créé avec succès (ID: {node.id}) dans la session {session_id}")
        return node.id
        
    except Exception as e:
        print(f"❌ Erreur création nœud session {session_id}: {e}")
        return None


def validate_session_exists(client, session_id):
    """
    Vérifie si une session existe dans PocketBase.
    
    Args:
        client: Client PocketBase
        session_id: ID de la session à vérifier
        
    Returns:
        bool: True si la session existe, False sinon
    """
    if not client or not session_id:
        return False
    
    try:
        session = client.collection("Session").get_one(session_id)
        return session is not None
    except Exception as e:
        print(f"❌ Session {session_id} introuvable: {e}")
        return False


def get_session_info(client, session_id):
    """
    Récupère les informations détaillées d'une session.
    
    Args:
        client: Client PocketBase
        session_id: ID de la session
        
    Returns:
        dict: Informations de la session ou None en cas d'erreur
    """
    if not validate_session_exists(client, session_id):
        return None
    
    try:
        session = client.collection("Session").get_one(session_id)
        return {
            "id": session.id,
            "scenario": getattr(session, 'scenario', None),
            "completed": getattr(session, 'completed', False),
            "created": getattr(session, 'created', None),
            "updated": getattr(session, 'updated', None)
        }
    except Exception as e:
        print(f"❌ Erreur récupération infos session {session_id}: {e}")
        return None
