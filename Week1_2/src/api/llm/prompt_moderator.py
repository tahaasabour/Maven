


from typing import Any, Protocol


class prompt_moderator(Protocol):
    def pre_redact_pii(self, text: str) -> str:...