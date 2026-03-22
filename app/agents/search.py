from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool

search = SerpAPIWrapper()
search_tool = Tool(
    name="google_search",
    description="Seach google for real-time information and news.",
    func=search.run
)

def search_agent(state):
    results = []

    for topic in state.plan:
        data = search.results(topic)
        results.extend(data)

    return {"search_results": results}