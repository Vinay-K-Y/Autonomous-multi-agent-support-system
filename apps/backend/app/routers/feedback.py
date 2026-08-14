from fastapi import APIRouter

from ai_core.calibration.outcome_store import mark_outcome
from app.schemas.feedback import EscalationOutcomeFeedback, EscalationOutcomeFeedbackResponse

router = APIRouter(
    prefix="/api/v1/feedback",
    tags=["Feedback"],
)


@router.post("/escalation-outcome", response_model=EscalationOutcomeFeedbackResponse)
async def submit_escalation_outcome(feedback: EscalationOutcomeFeedback):
    """Record whether a previously handled request's escalation decision
    was actually correct. This is the ground-truth signal that
    scripts/recalibrate_from_outcomes.py consumes to keep the calibrated
    threshold current — see ADAPTIVE_THRESHOLDS.md.

    In production this would typically be called by a human-review
    completion step (was the human review genuinely necessary?) or a
    ticket-resolution webhook (did a non-escalated request need a human
    after all?), not directly by an end user.
    """
    recorded = mark_outcome(
        request_id=feedback.request_id,
        outcome_correct=feedback.outcome_correct,
    )

    return EscalationOutcomeFeedbackResponse(
        request_id=feedback.request_id,
        recorded=recorded,
        message=(
            "Outcome recorded."
            if recorded
            else (
                "No matching un-labeled outcome record found for this "
                "request_id — it may not exist, or may already be labeled."
            )
        ),
    )
