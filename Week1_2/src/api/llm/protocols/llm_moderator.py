

from typing import Any, Protocol


class llm_moderator(Protocol):
    def moderate(self, data: dict) -> Any:...