from ai_session import AISession
from pocketbase import PocketBase
import threading


def start_ai_for_session(session, pb_client: PocketBase):
    ai = AISession(session.id, session.title, pb_client)
    threading.Thread(target=ai.start).start()