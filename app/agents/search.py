from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv

load_dotenv()

search = SerpAPIWrapper()

def search_agent(state):
    results = []
    for topic in state.plan[:3]:  # limit topics
        data = search.results(topic)

        organic = data.get("organic_results", [])

        for item in organic[:5]:  # limit results
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

    return {
        "search_results": results,
        "timeline": state.timeline + [f"🌐 Search: Found {len(results)} results"]
}