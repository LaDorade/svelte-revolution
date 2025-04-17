""" Exemple de Chat GPT
    Regarde un peu comment ça fonctionne """

from pocketbase import PocketBase
import os
from fastapi import FastAPI
from session_watcher import get_ai_sessions

app = FastAPI()
client = PocketBase("https://db.babel-revolution.fr")
PB_EMAIL = os.getenv("POCKETBASE_EMAIL")
PB_PASSWORD = os.getenv("POCKETBASE_PASSWORD")

@app.on_event("startup")
async def startup_event():
    print("🚀 Lancement du watcher de sessions")

@app.get("/sessions_ia_actives")
def get_active_ai_sessions():
    sessions_avec_ia = get_ai_sessions(client)

    # il reste à filtrer les sessions obtenues pour ne garder que celles qui sont actives
    # question: comment déterminer si une session est active ?

    return sessions_avec_ia
