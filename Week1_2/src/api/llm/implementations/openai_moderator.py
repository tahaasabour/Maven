
from typing import Any
from openai import OpenAI
import os


class openai_moderator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment variables")
        self.client = OpenAI(api_key=api_key)

    def moderate(self, data: dict) -> Any:
        text = data.get("body", "")
        if not text:
            return data
        
        try:
            response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=text
                )
            result = response.results[0]
            toxic = result.flagged  
            flags = [category for category, flagged in result.categories.items() if flagged]
        
        
            if toxic:
                data["moderation_flags"] = flags
                data["citations"] = data.get("citations", []) + ["abstain: moderation"]
                data["body"] = ""

            return data
        
        except Exception as e:
            raise RuntimeError(f"OpenAI moderation API call failed: {e}")