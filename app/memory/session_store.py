from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["synthra"]
collection = db["sessions"]

# ---------------- SAVE ----------------
def save_session(session_id, data):
    collection.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "session_id": session_id,   # ✅ ensure always present
                "data": data,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

# ---------------- LOAD ----------------
def load_sessions():
    sessions = {}

    for doc in collection.find():

        session_id = doc.get("session_id")

        # ✅ Case 1: New format (correct)
        if "data" in doc and isinstance(doc["data"], dict):
            sessions[session_id] = doc["data"]

        # 🔄 Case 2: Old format fallback (VERY IMPORTANT)
        else:
            sessions[session_id] = {
                "title": doc.get("query", "Old Session")[:40],
                "messages": [],
                "result": None,
                "stage": "input",
                "final_report": None
            }

    return sessions

# ---------------- DELETE ----------------
def delete_session(session_id):
    collection.delete_one({"session_id": session_id})