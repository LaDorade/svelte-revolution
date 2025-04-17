import asyncio
from ai_session import AISession
from utils import get_pocketbase_client, get_target_sessions

TARGET_SCENARIO_ID = "ald1jp16d9wkl1f"  # Scénario CMC

async def main():
    client = get_pocketbase_client()
    print("🔍 En attente de nouvelles sessions...")

    known_sessions = set()

    while True:
        sessions = get_target_sessions(client, TARGET_SCENARIO_ID)

        for session in sessions:
            if session.id not in known_sessions and session.id == "ii8eav18oai1e3t": #On force la session
                print(f"🚀 Nouvelle session détectée : {session.id}")
                known_sessions.add(session.id)

                #On créer une variable de type IASession avec le titre du scénario cible, on peut omdifier cette logique si jamais.
                # Avec aussi le client pocketbase
                ia = AISession(session.id, "Test", client)
                #Ensuite on vient lancer la tache avec aysncio et ia.start() méthode de la classe iasession qui lance le bail.
                asyncio.create_task(ia.start())

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
