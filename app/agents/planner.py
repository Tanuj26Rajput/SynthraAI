from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation"
)
model = ChatHuggingFace(llm=llm)

def planner_agent(state):
    query = state.query

    prompt = f'''
        Break this research query into 4-6 subtopics:
        Query: {query}'''
    
    response = model.invoke(prompt)
    plan = [line.strip() for line in response.content.split("\n") if line.strip()]
    return {"plan": plan}