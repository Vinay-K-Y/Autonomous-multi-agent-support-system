from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """
    Represents one tool invocation.
    """

    tool: str = Field(
        description="Name of the tool"
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )