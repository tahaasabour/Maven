


from typing import  Any, Protocol

class LLMProvider(Protocol):
    def create_client(self)-> Any: ...
    def call_model(self, client: Any, prompt: str, model: str, temperature: float) -> dict[str, Any]: ...