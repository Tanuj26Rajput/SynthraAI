from fastapi import APIRouter
from app.graph.builder import build_graph
from app.memory.memory import save_sessions
from app.agents.writer import writer_agent
from app.memory.memory import load_last_state
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

@router.post("/research/start")
def start_research(query: str, session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    result = graph.invoke({
        "query": query,
        "session_id": session_id
    })

    return {
        "session_id": session_id,
        "critique": result["critique"],
        "sources": result["ranked_sources"][:5],
        "message": "Approve or refine?"
    }

@router.post("/research/continue")
def continue_research(session_id: str, decision: str):
    state = load_last_state(session_id)

    if decision == "approve":
        update = writer_agent(state)
        state.final_report = update["final_report"]
        state.approved = True  # Optional: Mark as approved
        result = state
    else:
        state.refinement_count += 1
        result = graph.invoke(state)  # Assumes graph.invoke accepts GraphState

    save_sessions(session_id, result)
    return result