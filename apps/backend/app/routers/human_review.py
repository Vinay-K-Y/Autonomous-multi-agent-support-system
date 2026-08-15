from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai_core.calibration.outcome_store import load_all_outcomes, mark_outcome

router = APIRouter(prefix="/api/v1/human-review", tags=["Human Review"])


class ResolveHumanReview(BaseModel):
    was_necessary: bool  # did this request genuinely need a human?


@router.get("/pending")
async def list_pending_reviews():
    """Requests that were escalated but don't yet have a labeled outcome —
    i.e. nobody has confirmed whether the escalation was actually needed."""
    all_outcomes = load_all_outcomes()
    pending = [
        o for o in all_outcomes
        if o.was_escalated and o.outcome_correct is None
    ]
    return {"pending": pending, "count": len(pending)}


@router.post("/{request_id}/resolve")
async def resolve_human_review(request_id: str, resolution: ResolveHumanReview):
    recorded = mark_outcome(request_id=request_id, outcome_correct=resolution.was_necessary)
    if not recorded:
        raise HTTPException(
            status_code=404,
            detail=f"No pending outcome record found for request_id={request_id}",
        )
    return {"request_id": request_id, "recorded": True}
