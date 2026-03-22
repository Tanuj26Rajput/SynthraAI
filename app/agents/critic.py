from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
)
model = ChatHuggingFace(llm=llm)

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
    response = model.invoke(prompt)
    return {"critique": response.content}