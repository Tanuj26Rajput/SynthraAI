from pymongo import MongoClient
from datetime import datetime
from app.graph.state import GraphState

client = MongoClient("mongodb://localhost:27017/")
db = client["synthra"]
collection = db["sessions"]

def save_sessions(session_id, state):
    data = {
        "session_id": session_id,
        "state": state,
        "query": state.get("query"),
        "plan": state.get("plan"),
        "report": state.get("final_report"),
        "sources": state.get("ranked_sources"),
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(data)

def load_history(session_id):
    history = list(collection.find({"session_id": session_id}))
    return history

def load_last_state(session_id):
    data = collection.find_one(
        {"session_id": session_id},
        sort = [("timestamp", -1)]
    )
    return GraphState(**data["state"])