import pymupdf

doc = pymupdf.open()

# load the PDF file in to LangChain Documents(One per page)
# A LangChain-community 'SunSet' warning here is expected ; the Loader still works

from langchain_community.document_loaders import PyMuPDFLoader

pdf_file_path = "V5_Vendor_Profile.pdf"

loader = PyMuPDFLoader(pdf_file_path)
documents = loader.load()

documents[0].page_content

from typing import Annotated
import operator
from typing import TypedDict

class VendeorState(TypedDict):
    vendor_profile : str
    strengths : str
    risks : str
    scores : Annotated[list[int], operator.add]
    decision : str

from pydantic import BaseModel, Field

class Assessment(BaseModel):
    feedback: str = Field(description= "The assessment as short bullet points")
    score : int = Field(description= "Score from 0 to 10 for the aspect the prompt asks about", ge=0,le=0)

llm_with_structure = llm.with_structured_output(Assessment) 

# LLMs can through free tet . you can prompt to give output in structerd format but sometimes  they hallucinate and 
# Pydantic ensures that they give output in the required format only


