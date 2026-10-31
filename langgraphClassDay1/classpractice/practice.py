from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from langchain_core.output_parsers import StrOutputParser

import dotenv
import os
dotenv.load_dotenv()

#  Define the schema of the state
class ReturnState(TypedDict):
    vendor_Id: str
    units_sold: int
    units_returned: int
    return_rate: float
    rate_alert: str


#  Define the python function to calculate return rate
# This will become a node at the end.

def calculate_return_rate(state : ReturnState) -> ReturnState:

    # Read the values from the state
    sold = state["units_sold"]
    returned = state["units_returned"]   
    rate = round(returned/sold * 100, 2)

    # update the values of the state
    state["return_rate"]=rate

    return state

# Define the python function to generate alert based on return rate
def rate_alert(state: ReturnState)-> ReturnState:
    if state["return_rate"] < 8 :
        state["rate_alert"] = "normal"

    elif state["return_rate"] < 15:
        state["rate_alert"] = "Watch"
    else :
        state["rate_alert"] = "spike" 

    return state    


    

# Define the nodes and edges as a component of the graph

# Craeating graph
graph = StateGraph(ReturnState)

# Adding nodes to the graph
graph.add_node("calculate_return_rate", calculate_return_rate)
graph.add_node("rate_alert", rate_alert)

# Adding edges to the graph
graph.add_edge(START, "calculate_return_rate")
graph.add_edge("calculate_return_rate", "rate_alert")
graph.add_edge("rate_alert", END)

workflow = graph.compile()

# Run here to know the errors
# Now call the workflow with the input state and get the output state
input_state = {"vendor_Id": "V001", "units_sold": 100, "units_returned": 10}
output_state = workflow.invoke(input_state)
print(output_state)

