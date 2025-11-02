from pydantic import BaseModel, Field
from typing import  List, Dict



class GenResponse(BaseModel):
    title: str
    body: str
    style:str
    citations: List[str]=[]
    moderation_flags: List[str] = []
    tokens: Dict[str, int] = {}
    latency_ms: int = 0
    cost_est: float = 0.0
    request_id: str = ""


