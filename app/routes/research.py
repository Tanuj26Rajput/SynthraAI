from fastapi import APIRouter
from app.graph.builder import build_graph
from app.memory.memory import save_sessions
import uuid

router = APIRouter()
graph = build_graph()

@router.post("/research")
def run_search(query: str, session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    result = graph.invoke({
        "query": query,
        "session_id": session_id
    })

    save_sessions(session_id, result)
    
    return ({
        "session_id": session_id,
        "result": result
    })