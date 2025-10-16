import os
from pocketbase import PocketBase
from pocketbase.services.realtime_service import MessageData
from dotenv import load_dotenv
import time

def main():
    load_dotenv()
    PB_LOGIN = os.getenv("PB_LOGIN")
    PB_PASSWORD = os.getenv("PB_PASSWORD")

    if PB_LOGIN is None or PB_PASSWORD is None:
        raise ValueError("PB_LOGIN and PB_PASSWORD environment variables must be set.")

    client = PocketBase("https://db.babel-revolution.fr")
    client.admins.auth_with_password(PB_LOGIN, PB_PASSWORD)

    def handler(event: MessageData):
        print(f"Node event received: {event.action}, record id: {getattr(event.record, 'id', None)}")

    client.collection("Node").subscribe(handler)
    print("Subscribed to Node collection. Waiting for events...")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()