from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState

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
    builder.add_node("writer", writer_agent)

    def ranking_node(state):
        return {"ranked_sources": rank_sources(state.search_results)}
    
    builder.add_node("ranking", ranking_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "search")
    builder.add_edge("search", "ranking")
    builder.add_edge("ranking", "critic")

    def decision(state):
        if "APPROVED" in state.critique:
            return "writer"
        elif state.refinement_count < 2:
            return "search"
        else:
            return "writer"
        
    builder.add_conditional_edges("critic", decision)
    builder.add_edge("writer", END)
    return builder.compile()