
from .implementations.openai_provider import openai_provider
from .protocols.llm_provider import LLMProvider


class provider_factory:
    _providers:dict[str, LLMProvider] = {
        "openai": openai_provider(),
    }

    @classmethod
    def get_provider(cls, name: str) -> LLMProvider:
        provider =  cls._providers.get(name)
        if not provider:
            raise ValueError(f"Unsupported provider: {name}")
        return provider