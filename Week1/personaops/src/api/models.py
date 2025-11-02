from pydantic import BaseModel
from typing import List, Dict
import json, re

def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise ValueError("No JSON found in model output")
        return json.loads(m.group(0))

class GenRequest(BaseModel):
    input_text: str
    persona: str
    audience: str = "devs"
    length: int = 120
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    context: List[str] = []

class GenResponse(BaseModel):
    title: str
    body: str
    style: str
    citations: List[str] = []
    moderation_flags: List[str] = []
    tokens: Dict[str, int] = {}
    latency_ms: int = 0
    cost_est: float = 0.0
    request_id: str = ""