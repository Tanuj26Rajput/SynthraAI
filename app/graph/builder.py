from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState
from app.memory.memory import load_history

from app.agents.planner import planner_agent
from app.agents.search import search_agent
from app.agents.critic import critic_agent
from app.agents.writer import writer_agent
from app.tools.ranking import rank_sources

def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("planner", planner_agent)
    builder.add_node("search", search_agent)
    builder.add_node("critic", critic_agent)

    def ranking_node(state):
        return {
            "ranked_sources": rank_sources(state.search_results),
            "timeline": state.timeline + ["📊 Ranking: Ranked sources"]
        }
    builder.add_node("ranking", ranking_node)

    def load_memory_node(state):
        history = load_history(state.session_id)
        return {"history": history}
    builder.add_node("load_memory", load_memory_node)

    builder.add_edge(START, "load_memory")
    builder.add_edge("load_memory", "planner")
    builder.add_edge("planner", "search")
    builder.add_edge("search", "ranking")
    builder.add_edge("ranking", "critic")
        
    builder.add_edge("critic", END)
    return builder.compile()