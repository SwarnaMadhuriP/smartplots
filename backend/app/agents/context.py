from typing import Any, Protocol


class ToolContext(Protocol):
    state: dict[str, Any]