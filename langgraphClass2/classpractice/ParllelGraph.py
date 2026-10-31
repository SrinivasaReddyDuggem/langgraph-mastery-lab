
import dotenv
from langchain_openai import ChatOpenAI
import os

from typing import TypedDict

#==== Pattern 2 : Parllel Graph ====
# Task : run 3 independent listing checks at the same time , then write one report.
# Parallel nodes return ONLY the keys they changes; returning the whole state from
# Threee nodes in one step makes langraph stop with an InvalidUpdateError.

# Listing rules

TITLE_MAX = 60
REQUIRED_FIELDS = ["brand","Age_group", "fabric", "color","price"]
MIN_IMAGES=4

class ListingCheck(TypedDict):
    title: str
    fields: dict
    image_count: int
    title_check: dict
    fields_check: dict
    image_check: dict
    listing_report: str

# check 1 : Title is with in the character limit
def check_title(state:ListingCheck)-> ListingCheck:
    title = state["title"]
    n= len(state["title"])
    return {"title_check": {"ok": n<=TITLE_MAX, "details": f"Title has: {n} characters (limnit is {TITLE_MAX})"}}

# check 2 : Required fields are present
def check_fields(state:ListingCheck)-> ListingCheck:
    fields = state["fields"]
    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    return {"fields_check": {"ok": not missing, "details": "All required fields present" if not missing else f"Missing fields: {missing}"}}    

# check 3 : Enough images are present
def check_images(state:ListingCheck)-> ListingCheck:
    n = state["image_count"]
    return {"image_check": {"ok": n>=MIN_IMAGES, "details": f" {n} photos (minimum is {MIN_IMAGES})"}}


# check 4 : write a report based on the results of the 3 checks
def report(state:ListingCheck)-> ListingCheck:
   failed = [name for name, key in [("title", "title_check"), ("fields", "fields_check"), ("images", "image_check")]
              if not state[key]["ok"]]
   verdict = "READY for the dummy sites" if not failed else f"BLOCKED, fix:{', '.join(failed)} {failed}"
   return {"listing_report": verdict}

# create Graph
from langgraph.graph import StateGraph, START, END
graph = StateGraph(ListingCheck) 

graph.add_node("check_title", check_title)
graph.add_node("check_fields", check_fields)
graph.add_node("check_images", check_images)
graph.add_node("report", report)

graph.add_edge(START, "check_title")
graph.add_edge(START, "check_fields")
graph.add_edge(START, "check_images")

#graph.add_edge("check_title", "report")
#graph.add_edge("check_fields", "report")
#graph.add_edge("check_images", "report")

# Either this way or above way works, but the above is more compact and readable.
graph.add_edge(["check_title", "check_fields", "check_images"], "report")

graph.add_edge("report", END)


workflow = graph.compile()
initial_State = {"title": "This is a very long title that exceeds the maximum character limit for a listing",
                 "fields": {"brand": "Nike", "Age_group": "Adult", "fabric": "Cotton", "color": "Red"},
                 "image_count": 2} 

finalStatus = workflow.invoke(initial_State)
print(finalStatus)                 

 
