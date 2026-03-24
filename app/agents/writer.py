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

def writer_agent(state):
    data_summary = "\n".join([
        f"{i+1}. {s['title']} ({s['url']}): {s['snippet']}"
        for i, s in enumerate(state.ranked_sources[:3])
    ])
    
    prompt = f'''
        Write a COMPLETE professional research report.

        Requirements:
        - Clear headings
        - Bullet points where needed
        - Proper conclusion
        - No incomplete sentences

        Structure:
        1. Title
        2. Executive Summary
        3. Introduction
        4. Key Findings
        5. Analysis
        6. Conclusion
        7. References

        Query: {state.query}

        Sources:
        {data_summary}
    '''
    
    response = gemi_invoke(prompt)
    return {
        "final_report": response, 
        "timeline": state.timeline + ["✍️ Writer: Generated final report"]
    }
