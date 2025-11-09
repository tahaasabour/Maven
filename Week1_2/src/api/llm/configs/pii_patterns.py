import re

PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # emails
    re.compile(r"\b\+?\d[\d\s().-]{7,}\b"),                    # phones
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                              # API keys
]