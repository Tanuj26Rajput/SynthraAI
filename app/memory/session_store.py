from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime

client = MongoClient("mongodb+srv://Tanuj26Rajput:Tanuj1@cluster0.eilpujk.mongodb.net/gadgetry", serverSelectionTimeoutMS=2000)
db = client["synthra"]
collection = db["sessions"]

_memory_sessions = {}

# ---------------- SAVE ----------------
def save_session(session_id, data):
    _memory_sessions[session_id] = data

    try:
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
    except PyMongoError:
        pass

# ---------------- LOAD ----------------
def load_sessions():
    sessions = dict(_memory_sessions)

    try:
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
    except PyMongoError:
        return sessions

    return sessions

# ---------------- DELETE ----------------
def delete_session(session_id):
    _memory_sessions.pop(session_id, None)

    try:
        collection.delete_one({"session_id": session_id})
    except PyMongoError:
        pass