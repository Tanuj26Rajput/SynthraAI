from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["synthra"]
collection = client["sessions"]

def save_sessions(session_id, state):
    data = {
        "session_id": session_id,
        "query": state.query,
        "plan": state.plan,
        "report": state.final_report,
        "sources": state.ranked_sources,
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(data)

def load_history(session_id):
    history = list(collection.find({"session_id": session_id}))
    return history

