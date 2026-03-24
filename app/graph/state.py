from typing import List, Dict, Any
from pydantic import BaseModel

class GraphState(BaseModel):
    query: str
    plan: List[str] = []
    search_results: List[Dict[str, Any]] = []
    ranked_sources: List[Dict[str, Any]] = []
    critique: str = ""
    refinement_count: int = 0
    approved: bool = False
    final_report: str = ""
    history: List[Dict[str, Any]] = []
    session_id: str = ""
    timeline: list = []