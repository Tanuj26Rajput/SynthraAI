from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-exp",
#     temperature=0.7,
# )
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
def gemi_invoke(prompt: str) -> str:
    try:
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response or not response.text:
            return "fallback"   # ✅ safety

        return response.text.strip()

    except Exception as e:
        print("Gemini API Error:", e)
        return "fallback" 

def planner_agent(state):
    query = state.query
    history = state.history

    context = ""
    if history:
        context = f"Previous queries: {history[-2:]}"

    prompt = f'''
        context: {context}

        Break this research query into 4-6 subtopics:
        Query: {query}'''
    
    response = gemi_invoke(prompt)
    topics = [line.strip() for line in response.splitlines() if line.strip()]
    plan = []
    for topic in topics[1:]:
        plan.append(topic)
    return {
        "plan": plan,
        "timeline": state.timeline + ["🧠 Planner: Generated research plan"]
    }
