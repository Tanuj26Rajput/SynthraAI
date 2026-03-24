import uuid
from app.graph.builder import build_graph
from app.memory.memory import save_sessions
from app.agents.writer import writer_agent
from app.graph.state import GraphState
from app.agents.refiner import refinement_agent

def main():
    graph = build_graph()

    query = input("Enter your research query: ")
    session_id = str(uuid.uuid4())

    print(f"Starting research for query: {query}")
    print(f"Session ID: {session_id}")

    print("Invoking graph...")
    try:
        result = graph.invoke({
            "query": query,
            "session_id": session_id
        })
        print("Graph invocation completed.")
    except Exception as e:
        print(f"Error during graph invocation: {e}")
        return

    save_sessions(session_id, result)

    print("Research completed!")

    print("\n--- CRITIQUE ---")
    print(result["critique"])

    print("\n--- SOURCES ---")
    for s in result["ranked_sources"][:5]:
        print(f"{s['title']} - {s['url']}")
    

    while True:
        decision = input("\nApprove or refine? (approve/refine): ")

        if decision.lower() == "approve":
            state_obj = GraphState(**result)
            final = writer_agent(state_obj)
            print("\n--- FINAL REPORT ---")
            print(final["final_report"])
            break

        elif decision.lower() == "refine":
            print("\nRefining query...\n")
            state_obj = GraphState(**result)

            refined = refinement_agent(state_obj)

            state_obj.query = refined["query"]
            state_obj.refinement_count = refined["refinement_count"]

            if state_obj.refinement_count >= 2:
                print("Max refinement head. Proceeding to final report.")
                break

            print(f"\nNew Query: {state_obj.query}\n")

            result = graph.invoke(state_obj)

            print("\n---New Critique---\n")
            print(result["critique"])

            print("\n--- NEW SOURCES ---")
            for s in result["ranked_sources"][:5]:
                print(f"{s['title']} - {s['url']}")

        else:
            print("Invalid input. Type approve/refine.")


if __name__ == "__main__":
    main()