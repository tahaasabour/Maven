

from pydantic import BaseModel, Field
from .personas import PersonaType

class GenerateRequest(BaseModel):
    input_text: str
    persona: PersonaType
    length: int = 0
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o-mini")
    context:list[str]= Field(default_factory=list)
    audience: str = Field(default="general")
