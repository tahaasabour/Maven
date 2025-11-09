

from typing import Any
import time
import uuid
from .provider_factory import provider_factory
from .model_prices import MODEL_PRICES
import json

class llm_service:
    def call_model(self, payload: dict[str, Any]) -> dict[str, Any]:
        start_time = time.time()
        provider = payload.get("provider")
        if not provider:
            raise ValueError("Provider not specified in payload")
        provider = provider_factory.get_provider(provider)
        client = provider.create_client()
        response = provider.call_model(
            client=client,
            prompt=payload.get("prompt"),
            model=payload.get("model"),
            temperature=payload.get("temperature", 0.7)
        )
        elapsed_time = int((time.time() - start_time))
        try:
            data  = response.get("text","")
            data = json.loads(data)
        except Exception as e:
            raise RuntimeError(f"Error processing response as JSON: {e}")
        
        usage = response.get("usage", None)
        tokens = {"prompt": 0, "completion": 0}
        if usage:
            if isinstance(usage, dict):
                tokens["prompt"] = usage.get("prompt_tokens", 0)
                tokens["completion"] = usage.get("completion_tokens", 0)
            else:
                tokens["prompt"] = getattr(usage, "prompt_tokens", 0) or 0
                tokens["completion"] = getattr(usage, "completion_tokens", 0) or 0  



       

        price = MODEL_PRICES.get(payload.get("model"), {"in": 0, "out": 0}) 
        cost_est = round((tokens["prompt"] * price["in"] + tokens["completion"] * price["out"]) / 1000.0, 6)
        
       
        
        return {
        **data,
        "tokens": tokens,
        "latency_ms": elapsed_time,
        "cost_est": cost_est,
        "request_id": str(uuid.uuid4()),
        "moderation_flags": data.get("moderation_flags", []),
    }