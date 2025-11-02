import re

PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # emails
    re.compile(r"\b\+?\d[\d\s().-]{7,}\b"),                    # phones
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                              # API keys
]

def pre_redact_pii(text: str) -> str:
    red = text
    for pat in PII_PATTERNS:
        red = pat.sub("***", red)
    return red

def post_moderate(data: dict) -> dict:
    """Simple moderation logic - expand as needed"""
    flags = []
    toxic = False  # Add OpenAI moderation API call here
    
    if toxic:
        data["moderation_flags"] = flags
        data["citations"] = data.get("citations", []) + ["abstain: moderation"]
        data["body"] = ""
    return data