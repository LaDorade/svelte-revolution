import os
import asyncio
from dotenv import load_dotenv
from pocketbase import PocketBase

load_dotenv()

def get_pocketbase_client():
    pb = PocketBase("https://db.babel-revolution.fr")
    admin_data = pb.admins.auth_with_password(os.getenv("POCKETBASE_EMAIL"), os.getenv("POCKETBASE_PASSWORD"))
    return pb

def get_target_sessions(client, scenario_id):
    all_sessions = client.collection("Session").get_full_list()
    return [s for s in all_sessions if s.scenario == scenario_id]

async def get_nodes_for_session(client, session_id):
    return await client.collection("Node").get_full_list({
        "filter": f"session = '{session_id}'"
    })

async def post_node_to_session(client, session_id, text):
    await client.collection("Node").create({
        "session": session_id,
        "content": text,
        "author": "ia_mistral"
    })
