
from ..configs.pii_patterns import PII_PATTERNS

class general_prompt_moderator:
    def pre_redact_pii(self, text: str) -> str:
        red = text
        for pat in PII_PATTERNS:
            red = pat.sub("***", red)
        return red
