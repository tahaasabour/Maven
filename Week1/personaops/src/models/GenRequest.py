from pydantic import BaseModel, Field
from typing import List, Dict

class GenRequest(BaseModel):
    input_text:str
    persona:str
    audience:str
    lenght:int 
    provider:str
    model:str ="gpt-4o-mini"
    context: List[str]=[]