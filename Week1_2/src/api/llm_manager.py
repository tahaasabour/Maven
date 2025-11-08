
import os
import time
from .utils import extract_json
import uuid



def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set in environment variables")
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize OpenAI client: {e}")



_PROVIDER_FACTORIES = {
    "openai": get_openai_client,
}


def get_provider_client(provider_name: str):
    factory = _PROVIDER_FACTORIES.get(provider_name)
    if not factory:
        raise ValueError(f"Unsupported provider: {provider_name}")
    return factory()


def call_openai(client, prompt: str, model: str, temperature: float):
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    txt = getattr(resp.choices[0].message, "content", None) or resp.choices[0].message.content
    usage = getattr(resp, "usage", None)
    return {"text": txt, "usage": usage, "raw": resp}


_PROVIDER_CALLERS = {
    "openai": call_openai
}


def call_model(payload: dict) -> dict:
    t0 = time.time()
    provider_name = payload["provider"]
    if not provider_name:
        raise ValueError("Provider not specified in payload")
    client = get_provider_client(provider_name)
    if not client:
        raise RuntimeError(f"Failed to initialize client for provider: {provider_name}")
    caller = _PROVIDER_CALLERS.get(provider_name)
    if not caller:
        raise ValueError(f"No caller function for provider: {provider_name}")
    
    try:
        response = caller(client=client, prompt=payload.get("prompt"),
                         model=payload.get("model"), 
                         temperature=payload.get("temperature", 0.7))
        print("LLM response:", response)
    except Exception as e:
        raise RuntimeError(f"LLM provider error: {e}")
    
    elapsed = int((time.time() - t0) * 1000)
    
    try:
        txt = response["text"]
        data  =  extract_json(txt)
    except Exception:
        raise RuntimeError("Failed to parse model output as JSON")
    
    try:
        usage = response.get("usage", None)
        tokens = {"prompt": 0, "completion": 0}
        if usage:
            prompt_tokens = getattr(usage, "prompt_tokens", None) or usage.get("prompt_tokens") if isinstance(usage, dict) else None
            completion_tokens = getattr(usage, "completion_tokens", None) or usage.get("completion_tokens") if isinstance(usage, dict) else None
            tokens["prompt"] = prompt_tokens or 0
            tokens["completion"] = completion_tokens or 0

        MODEL_PRICES = {
         "gpt-4o-mini": {"in": 0.00015, "out": 0.0006},
        }

        price = MODEL_PRICES.get(payload.get("model"), {"in": 0, "out": 0})
        cost = (tokens["prompt"] * price["in"] + tokens["completion"] * price["out"]) / 1000.0

        data["tokens"] = tokens
        data["latency_ms"] = elapsed
        data["cost_est"] = round(cost, 6)
        data["request_id"] = str(uuid.uuid4())
        data["moderation_flags"] = data.get("moderation_flags", [])
        return data
    except Exception as e:
        raise RuntimeError(f"Error processing model response data: {e}")
