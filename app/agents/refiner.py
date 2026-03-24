from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
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

# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-exp",
#     temperature=0.7,
# )

def refinement_agent(state):
    query = state.query
    critique = state.critique

    prompt = f"""
        Original query:
        {query}

        Critique:
        {critique}

        Improve the query to address the issues.
        Make it more specific, complete and high quality
    """
    response = gemi_invoke(prompt)
    return {
        "query": response,
        "refinement_count": state.refinement_count + 1,
        "timeline": state.timeline + ["🔁 Refiner: Improved query"]
    }
