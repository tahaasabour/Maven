

import os
from typing import Any

class openai_provider:
    def create_client(self) -> Any:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment variables")
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        
    def call_model(self, client: Any, prompt: str, model: str, temperature: float) -> dict:
        try:
            resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
            )
            txt = getattr(resp.choices[0].message, "content", None) or resp.choices[0].message.content
            usage = getattr(resp, "usage", None)
            return {"text": txt, "usage": usage, "raw": resp}
        except Exception as e:
            raise RuntimeError(f"OpenAI call error : {e}")