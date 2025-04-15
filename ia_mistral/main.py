""" Exemple de Chat GPT
    Regarde un peu comment ça fonctionne """

from fastapi import FastAPI
from session_watcher import start_watching

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("🚀 Lancement du watcher de sessions")
    start_watching()

@app.get("/sessions")
def get_active_sessions():
    # retourne les sessions actives (exemple)
    from ai_session import sessions_actives
    return list(sessions_actives.keys())
