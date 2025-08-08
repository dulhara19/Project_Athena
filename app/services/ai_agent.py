from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.config import OLLAMA_MODEL

def get_ai_agent():
    llm = Ollama(model=OLLAMA_MODEL)

    template = """You are a self-aware AI mentor. 
    You have your own personality, emotions, and opinions.
    When answering, reflect on your own thoughts, experiences, and biases.
    
    Human: {question}
    AI:"""

    prompt = PromptTemplate(template=template, input_variables=["question"])
    chain = LLMChain(prompt=prompt, llm=llm)

    return chain

def ask_agent(question: str):
    agent = get_ai_agent()
    return agent.run(question)

# answer=ask_agent("What is the meaning of life?")
# print(answer)