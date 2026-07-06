from pydantic import BaseModel, Field

from ai_core.models.execution_plan import ExecutionPlan


class DecisionResult(BaseModel):
    """
    Result of validating an execution plan.
    """

    approved: bool = True

    reasoning: str = ""

    modified_plan: ExecutionPlan | None = None

    blocked_tools: list[str] = Field(default_factory=list)