
from pydantic import BaseModel, Field
from .personas import PersonaType

class GenerateResponse(BaseModel):
    title:str
    body:str
    style:PersonaType
    citations:list[str]= Field(default_factory=[])
    moderation_flags:list[str]= Field(default_factory=[])
    tokens:dict[str,int]= Field(default_factory=dict)
    latency_ms:int = Field(default=0)
    cost_est:float = Field(default=0.0)
    request_id:str = Field(default="")