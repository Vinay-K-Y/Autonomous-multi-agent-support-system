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
