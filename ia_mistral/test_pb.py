from pocketbase import PocketBase
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

"""
Script de test de résilience pour PocketBase.
Teste l'ajout massif de nœuds pour vérifier la stabilité du système.

Structure d'un TriggerNode dans la BDD:
id: int
scenario: int
infos: json
{
  "id":
  "conditions": [],
  "triggers": [],
  "title":
  "text":
  "author":
}
created: date
updated: date
"""

def create_single_node(client, session_id, parent_id, side_id, node_index):
    """Crée un seul nœud avec gestion d'erreurs."""
    try:
        start_time = time.time()
        
        client.collection("Node").create({
            "title": f"Test Node #{node_index}",
            "text": f"Ceci est le nœud de test numéro {node_index} - {time.strftime('%H:%M:%S')}",
            "author": f"TestBot-{node_index % 5}",  # Varie les auteurs
            "type": "contribution",
            "session": session_id,
            "parent": parent_id,
            "side": side_id,
        })
        
        elapsed = time.time() - start_time
        return {"success": True, "index": node_index, "time": elapsed}
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {"success": False, "index": node_index, "error": str(e), "time": elapsed}

def test_mass_node_creation(client, session_id, parent_id, side_id, num_nodes=100, max_workers=10):
    """Teste la création massive de nœuds avec threading."""
    print(f"🚀 Début du test de résilience - {num_nodes} nœuds avec {max_workers} threads")
    
    start_time = time.time()
    successes = 0
    failures = 0
    total_api_time = 0
    errors = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumet toutes les tâches
        future_to_index = {
            executor.submit(create_single_node, client, session_id, parent_id, side_id, i): i 
            for i in range(num_nodes)
        }
        
        # Traite les résultats au fur et à mesure
        for future in as_completed(future_to_index):
            result = future.result()
            total_api_time += result["time"]
            
            if result["success"]:
                successes += 1
                if successes % 10 == 0:
                    print(f"✅ {successes}/{num_nodes} nœuds créés avec succès")
            else:
                failures += 1
                errors.append(f"Node {result['index']}: {result['error']}")
                print(f"❌ Erreur node {result['index']}: {result['error']}")
    
    total_time = time.time() - start_time
    
    # Rapport final
    print(f"\n📊 RAPPORT DE TEST:")
    print(f"   • Total de nœuds tentés: {num_nodes}")
    print(f"   • Succès: {successes} ({successes/num_nodes*100:.1f}%)")
    print(f"   • Échecs: {failures} ({failures/num_nodes*100:.1f}%)")
    print(f"   • Temps total: {total_time:.2f}s")
    print(f"   • Temps moyen par API: {total_api_time/num_nodes:.3f}s")
    print(f"   • Débit: {num_nodes/total_time:.1f} nœuds/seconde")
    
    if errors:
        print(f"\n❌ ERREURS DÉTECTÉES ({len(errors)}):")
        for error in errors[:5]:  # Affiche les 5 premières erreurs
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   • ... et {len(errors) - 5} autres erreurs")
    
    return successes, failures

def test_sequential_creation(client, session_id, parent_id, side_id, num_nodes=50):
    """Teste la création séquentielle pour comparaison."""
    print(f"🐌 Test séquentiel - {num_nodes} nœuds")
    
    start_time = time.time()
    successes = 0
    failures = 0
    
    for i in range(num_nodes):
        result = create_single_node(client, session_id, parent_id, side_id, i + 1000)
        
        if result["success"]:
            successes += 1
        else:
            failures += 1
            print(f"❌ Erreur node {result['index']}: {result['error']}")
        
        if (i + 1) % 10 == 0:
            print(f"📈 {i + 1}/{num_nodes} traités")
    
    total_time = time.time() - start_time
    print(f"📊 Test séquentiel terminé: {successes}/{num_nodes} en {total_time:.2f}s")
    
    return successes, failures

if __name__ == "__main__":
    # Configuration du test
    SESSION_ID = "h95i580pr0eeowi"
    PARENT_ID = "3i595vvsra1zkiy"
    SIDE_ID = "k307wt00z8j5onj"
    
    try:
        load_dotenv()
        PB_LOGIN = os.getenv("PB_LOGIN")
        PB_PASSWORD = os.getenv("PB_PASSWORD")
        
        if not PB_LOGIN or not PB_PASSWORD:
            print("❌ Variables d'environnement manquantes")
            exit(1)
            
    except Exception as e:
        print(f"❌ Erreur chargement .env: {e}")
        exit(1)

    try:
        print("🔌 Connexion à PocketBase...")
        client = PocketBase("https://db.babel-revolution.fr")
        client.admins.auth_with_password(PB_LOGIN, PB_PASSWORD)
        print("✅ Connexion réussie")
        
        # Test de base - quelques nœuds
        print("\n=== TEST 1: Création de base (10 nœuds) ===")
        success, fail = test_sequential_creation(client, SESSION_ID, PARENT_ID, SIDE_ID, 10)
        
        if success == 10:
            print("✅ Test de base réussi, passage aux tests de charge")
            
            # Test de charge modéré
            print("\n=== TEST 2: Charge modérée (50 nœuds, 5 threads) ===")
            test_mass_node_creation(client, SESSION_ID, PARENT_ID, SIDE_ID, 50, 5)
            
            # Test de charge intensive
            print("\n=== TEST 3: Charge intensive (100 nœuds, 10 threads) ===")
            test_mass_node_creation(client, SESSION_ID, PARENT_ID, SIDE_ID, 100, 10)
            
            # Test extrême (optionnel)
            user_input = input("\n🤔 Voulez-vous tester la charge extrême (500 nœuds)? [y/N]: ")
            if user_input.lower() == 'y':
                print("\n=== TEST 4: Charge EXTRÊME (500 nœuds, 15 threads) ===")
                test_mass_node_creation(client, SESSION_ID, PARENT_ID, SIDE_ID, 500, 15)
        else:
            print("❌ Test de base échoué, arrêt des tests")
            
    except Exception as e:
        print(f"❌ Erreur Pocketbase: {e}")
        
    print("\n🏁 Tests de résilience terminés!")