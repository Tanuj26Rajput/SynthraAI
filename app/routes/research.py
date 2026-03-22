from fastapi import APIRouter
from app.graph.builder import build_graph

router = APIRouter()
graph = build_graph()

@router.post("/research")
def run_search(query: str):
    result = graph.invoke({"query": query})
    return result