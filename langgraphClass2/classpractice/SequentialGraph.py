import dotenv
from langchain_openai import ChatOpenAI
import os

from typing import TypedDict

dotenv.load_dotenv(".env")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# LLM
api_key = os.getenv("OPENROUTER_API_KEY")
model = ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )

# ============= Pattern 1.Sequential Graph ==============
# Task : turn V5 's messy vendor text into a size note a parent can use
# Node 1 Extracts the size info , node2 writes the note : one node's output feeds into the next.

from typing import TypedDict
class SizeNote(TypedDict):
    raw_listing : str
    size_info: str
    size_note: str

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# Node 1 : Extract size info from the raw listing
def extract_sizes(state:SizeNote)-> SizeNote:
    raw = state["raw_listing"]
    prompt = PromptTemplate(
        template="Read this vendor listing text and write the size information , in one short sentence:{raw}",
        input_variables=["raw"]
    )

    chain = prompt | model | StrOutputParser()
    result = chain.invoke({"raw": raw})
    state["size_info"] = result
    return state

# Node 2 : turn the size info into 3 bullet points that help a parent pick a size
def write_size_note(state:SizeNote)-> SizeNote:
    info = state["size_info"]
    prompt = PromptTemplate(
        template="using these size details :{info}, write 3 bullet points that help a partent to choose the " \
        "right size for their child. Make it short and easy to read.",
        input_variables=["info"]
    )

    chain = prompt | model | StrOutputParser()
    result = chain.invoke({"info": info})
    state["size_note"] = result
    return state

 # create the graph
from langgraph.graph import StateGraph, START, END
graph = StateGraph(SizeNote)

graph.add_node("extract_sizes", extract_sizes)
graph.add_node("write_size_note", write_size_note)
graph.add_edge(START, "extract_sizes")
graph.add_edge("extract_sizes", "write_size_note") 
graph.add_edge("write_size_note", END)

workflow = graph.compile()


from IPython.display import Image, display
display(Image(workflow.get_graph().draw_mermaid_png()))

initial_State = {"raw_listing": "boys cotton dino tee. Color : green, Tag Size: 105 (CN , height in cm ) "
"chest 56 cm Machine wash cold"}
final_State  = workflow.invoke(initial_State)
print(final_State)