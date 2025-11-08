
import json
import re

def extract_json(text: str) -> dict:
    """Extract JSON from model output."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise ValueError("No JSON found in model output")
        return json.loads(m.group(0))
