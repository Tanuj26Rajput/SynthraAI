from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
)
model = ChatHuggingFace(llm=llm)

def writer_agent(state):
    prompt = f'''
        Write a structured research report based on:

        Query: {state.query}
        Data: {state.ranked_sources[:5]}
        '''
    response = model.invoke(prompt)
    return {"final_report": response.content}