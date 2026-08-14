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

    # The escalation confidence threshold actually used for this decision
    # (calibrated or static default — see ai_core/calibration/provider.py).
    # Recorded so it can be logged alongside the outcome for later
    # recalibration; see ai_core/calibration/outcome_store.py.
    escalation_threshold_used: float | None = None