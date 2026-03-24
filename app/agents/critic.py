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

def critic_agent(state):
    data = state.ranked_sources[:5]

    prompt = f'''
        Evaluate this research data:
        {data}

        check:
        - is it sufficient?
        - any bias?
        - missing perspectives?

        respond with:
        APPROVED or REVISE + reason
        '''
    response = gemi_invoke(prompt)
    return {
        "critique": response,
        "awaiting_approval": True,
        "timeline": state.timeline + ["🧐 Critic: Evaluated research quality"]
    }
