from pydantic import BaseModel, Field


class EscalationOutcomeFeedback(BaseModel):
    """Ground-truth label for a previously handled request, used to
    recalibrate the escalation threshold over time. See
    ADAPTIVE_THRESHOLDS.md for who/what is expected to call this and when.
    """

    request_id: str = Field(
        description="The request_id returned in SupportResponse for the original request."
    )
    outcome_correct: bool = Field(
        description=(
            "Was the escalation decision correct? True if: (a) the request "
            "WAS escalated and a human genuinely needed to handle it, or "
            "(b) the request was NOT escalated and it was resolved without "
            "any human follow-up being needed. False if the decision was "
            "wrong in either direction (escalated something trivial, or "
            "failed to escalate something that needed a human)."
        )
    )


class EscalationOutcomeFeedbackResponse(BaseModel):
    request_id: str
    recorded: bool
    message: str
