from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph import graph
from langgraph.graph import StateGraph, START, END

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os
load_dotenv()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

api_key = os.getenv("OPENROUTER_API_KEY")
model = ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )

class LLMState(TypedDict):
    input_text: str
    output_text: str

def llm_query(state:LLMState)-> LLMState:
    query = state["input_text"]
    prompt = f"Explain {query} in one sentence."
    chain =  model | StrOutputParser()
    result = chain.invoke(prompt) 
    state["output_text"] = result
    return state

graph = StateGraph(LLMState)
graph.add_node("llm_query", llm_query)
graph.add_edge(START, "llm_query")
graph.add_edge("llm_query", END)

workflow = graph.compile()
initial_State = {"input_text": "REST API"}
final_State  = workflow.invoke(initial_State)
print(final_State)
                   