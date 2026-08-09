from typing import List

from pydantic import BaseModel, Field

from ai_core.models.tool_call import ToolCall


class ExecutionPlan(BaseModel):
    """
    Planner output.
    """

    reasoning: str

    tool_calls: List[ToolCall] = Field(
        default_factory=list
    )

    used_fallback: bool = False