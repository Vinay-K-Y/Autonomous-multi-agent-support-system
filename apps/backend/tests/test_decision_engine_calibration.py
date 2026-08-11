"""Proves the calibration integration actually changes DecisionEngine
behavior — not just that the calibration module works in isolation.

Covers:
  1. With no calibration artifact on disk, DecisionEngine.should_escalate
     uses the static settings.ESCALATION_THRESHOLD, unchanged from before
     calibration existed (backward compatibility).
  2. With a valid (non-fallback) calibration artifact present, the
     calibrated threshold is used instead, and it actually changes the
     escalation decision at a confidence level where the two thresholds
     disagree.
  3. A calibration artifact whose own run fell back is treated the same
     as no artifact at all — it must never silently suppress escalation.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_core.calibration.models import CalibrationArtifact
from ai_core.calibration.provider import CalibratedThresholdProvider
from ai_core.calibration.store import save_calibration_artifact
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.intent import IntentOutput, IntentType
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine
from app.core.config import settings


def build_state(confidence: float) -> SupportState:
    state = SupportState(
        request=CustomerRequest(message="My order hasn't arrived"),
        metadata=ProcessingMetadata(request_id="REQ-CALIBRATION-TEST"),
    )
    state.intent = IntentOutput(
        intent=IntentType.DELIVERY, confidence=confidence, reasoning="test"
    )
    state.execution_plan = ExecutionPlan(reasoning="Initial plan", tool_calls=[])
    return state


def _valid_artifact(threshold: float) -> CalibrationArtifact:
    return CalibrationArtifact(
        threshold=threshold,
        target_risk=0.15,
        delta=0.05,
        calibration_set_size=300,
        n_accepted_at_threshold=99,
        coverage=0.33,
        empirical_risk_at_threshold=0.10,
        risk_upper_bound_at_threshold=0.14,
        fallback_used=False,
        fallback_reason=None,
        computed_at=datetime.now(UTC).isoformat(),
        source_dataset="test-fixture",
    )


def _fallback_artifact() -> CalibrationArtifact:
    return CalibrationArtifact(
        threshold=1.0,
        target_risk=0.05,
        delta=0.05,
        calibration_set_size=10,
        n_accepted_at_threshold=0,
        coverage=0.0,
        empirical_risk_at_threshold=0.0,
        risk_upper_bound_at_threshold=0.0,
        fallback_used=True,
        fallback_reason="calibration set too small",
        computed_at=datetime.now(UTC).isoformat(),
        source_dataset="test-fixture",
    )


def test_no_artifact_falls_back_to_static_config_threshold(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.json"
    provider = CalibratedThresholdProvider(artifact_path=missing_path)
    engine = DecisionEngine(threshold_provider=provider)

    # settings.ESCALATION_THRESHOLD is 0.7 by default (see app/core/config.py);
    # confidence just below it should escalate exactly as it did before
    # calibration was introduced.
    state = build_state(confidence=settings.ESCALATION_THRESHOLD - 0.05)
    result = engine.evaluate(state)
    human_review_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "human_review"]
    assert len(human_review_tools) == 1
    assert "static config default" in human_review_tools[0].parameters["reason"]


def test_valid_calibrated_artifact_overrides_static_threshold(tmp_path: Path) -> None:
    artifact_path = tmp_path / "calibrated_thresholds.json"
    # Calibrated threshold (0.55) is deliberately LOWER than the static
    # default (0.7) — a confidence of 0.6 would escalate under the static
    # default but should NOT escalate once calibration says 0.55 is safe.
    save_calibration_artifact(_valid_artifact(threshold=0.55), artifact_path)

    provider = CalibratedThresholdProvider(artifact_path=artifact_path)
    engine = DecisionEngine(threshold_provider=provider)

    state = build_state(confidence=0.6)
    result = engine.evaluate(state)
    human_review_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "human_review"]

    assert len(human_review_tools) == 0, (
        "Expected calibrated threshold (0.55) to be used instead of the "
        "static default (0.7) — confidence 0.6 should NOT escalate."
    )


def test_valid_calibrated_artifact_still_escalates_below_its_own_threshold(tmp_path: Path) -> None:
    artifact_path = tmp_path / "calibrated_thresholds.json"
    save_calibration_artifact(_valid_artifact(threshold=0.55), artifact_path)

    provider = CalibratedThresholdProvider(artifact_path=artifact_path)
    engine = DecisionEngine(threshold_provider=provider)

    state = build_state(confidence=0.4)
    result = engine.evaluate(state)
    human_review_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "human_review"]

    assert len(human_review_tools) == 1
    assert "calibrated threshold" in human_review_tools[0].parameters["reason"]


def test_fallback_artifact_is_treated_as_no_artifact(tmp_path: Path) -> None:
    artifact_path = tmp_path / "calibrated_thresholds.json"
    save_calibration_artifact(_fallback_artifact(), artifact_path)

    provider = CalibratedThresholdProvider(artifact_path=artifact_path)
    engine = DecisionEngine(threshold_provider=provider)

    # A fallback artifact must never suppress escalation. Confidence just
    # below the static threshold must still escalate, exactly as if no
    # artifact existed at all.
    state = build_state(confidence=settings.ESCALATION_THRESHOLD - 0.05)
    result = engine.evaluate(state)
    human_review_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "human_review"]

    assert len(human_review_tools) == 1
    assert "static config default" in human_review_tools[0].parameters["reason"]
