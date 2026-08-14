from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CalibrationExample(BaseModel):
    """One raw calibration example: a labeled support message plus what the
    intent classifier actually predicted for it, collected by running the
    real IntentAgent against a held-out labeled dataset (see
    scripts/collect_calibration_data.py)."""

    message: str
    true_intent: str
    predicted_intent: str
    confidence: float = Field(ge=0, le=1)

    @property
    def correct(self) -> bool:
        return self.true_intent == self.predicted_intent


class CalibrationArtifact(BaseModel):
    """Persisted result of a calibration run. This is what
    CalibratedThresholdProvider loads at runtime instead of relying on the
    hand-picked ESCALATION_THRESHOLD config constant."""

    threshold: float
    target_risk: float
    delta: float
    calibration_set_size: int
    n_accepted_at_threshold: int
    coverage: float
    empirical_risk_at_threshold: float
    risk_upper_bound_at_threshold: float
    fallback_used: bool
    fallback_reason: Optional[str] = None
    computed_at: str  # ISO 8601 timestamp
    source_dataset: str


class OutcomeRecord(BaseModel):
    """One production outcome record: what confidence/threshold governed a
    real request's escalation decision, and — once known — whether that
    decision was actually correct.

    `outcome_correct` is intentionally optional: it starts as None when the
    request is logged (we don't yet know if escalating, or not escalating,
    was the right call) and gets filled in later once ground truth arrives
    — e.g. a human reviewer confirms an escalated request genuinely needed
    a human, or a non-escalated request's ticket closes without any
    follow-up escalation. Records with outcome_correct=None are excluded
    from recalibration until they're labeled — see outcome_store.py.
    """

    request_id: str
    confidence: float = Field(ge=0, le=1)
    threshold_used: float
    was_escalated: bool
    outcome_correct: Optional[bool] = None
    logged_at: str  # ISO 8601 timestamp, when the request was handled
    labeled_at: Optional[str] = None  # ISO 8601 timestamp, when outcome_correct was set

    def to_calibration_record(self):
        """Convert to the (confidence, correct) shape select_calibrated_threshold
        expects. Only valid once outcome_correct is no longer None."""
        from ai_core.calibration.selective_risk import CalibrationRecord

        if self.outcome_correct is None:
            raise ValueError(
                f"OutcomeRecord {self.request_id} has no labeled outcome yet; "
                "cannot use in recalibration."
            )
        return CalibrationRecord(confidence=self.confidence, correct=self.outcome_correct)
