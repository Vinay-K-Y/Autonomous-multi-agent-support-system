"""Compute a statistically calibrated escalation threshold from a set of
labeled calibration examples, and write it as the artifact that
CalibratedThresholdProvider loads at runtime.

This step requires NO network access and NO LLM calls — it only does
statistics over already-collected (confidence, correct) pairs. Run
scripts/collect_calibration_data.py first to produce those pairs from
real IntentAgent predictions.

Usage:
    python scripts/compute_calibrated_threshold.py \
        --examples ai_core/calibration/data/calibration_examples.jsonl \
        --target-risk 0.10 \
        --delta 0.05

Writes ai_core/calibration/data/calibrated_thresholds.json by default.
DecisionEngine.should_escalate() picks this up automatically the next
time the process starts (or call CalibratedThresholdProvider.reload()).
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from ai_core.calibration.models import CalibrationArtifact
from ai_core.calibration.selective_risk import CalibrationRecord, select_calibrated_threshold
from ai_core.calibration.store import (
    DEFAULT_ARTIFACT_PATH,
    DEFAULT_EXAMPLES_PATH,
    load_calibration_examples,
    save_calibration_artifact,
)
from app.core.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--target-risk", type=float, default=settings.CALIBRATION_TARGET_RISK)
    parser.add_argument("--delta", type=float, default=settings.CALIBRATION_DELTA)
    parser.add_argument("--min-calibration-size", type=int, default=30)
    args = parser.parse_args()

    examples = load_calibration_examples(args.examples)
    if not examples:
        raise SystemExit(
            f"No calibration examples found at {args.examples}. "
            "Run scripts/collect_calibration_data.py first."
        )

    records = [
        CalibrationRecord(confidence=e.confidence, correct=e.correct) for e in examples
    ]

    outcome = select_calibrated_threshold(
        records,
        target_risk=args.target_risk,
        delta=args.delta,
        min_calibration_size=args.min_calibration_size,
    )

    artifact = CalibrationArtifact(
        threshold=outcome.threshold,
        target_risk=outcome.target_risk,
        delta=outcome.delta,
        calibration_set_size=outcome.calibration_set_size,
        n_accepted_at_threshold=outcome.n_accepted_at_threshold,
        coverage=outcome.coverage,
        empirical_risk_at_threshold=outcome.empirical_risk_at_threshold,
        risk_upper_bound_at_threshold=outcome.risk_upper_bound_at_threshold,
        fallback_used=outcome.fallback_used,
        fallback_reason=outcome.fallback_reason,
        computed_at=datetime.now(UTC).isoformat(),
        source_dataset=str(args.examples),
    )

    save_calibration_artifact(artifact, args.output)

    print(f"Calibration set size: {artifact.calibration_set_size}")
    if artifact.fallback_used:
        print(f"FALLBACK: {artifact.fallback_reason}")
        print("Wrote a fallback artifact -> DecisionEngine will use the static "
              "ESCALATION_THRESHOLD config value until this is resolved.")
    else:
        print(f"Calibrated threshold: {artifact.threshold:.4f}")
        print(f"Coverage (fraction not escalated): {artifact.coverage:.4f}")
        print(f"Empirical risk at threshold: {artifact.empirical_risk_at_threshold:.4f}")
        print(f"Risk upper bound (guarantee): {artifact.risk_upper_bound_at_threshold:.4f} "
              f"<= target {artifact.target_risk:.4f}")
    print(f"Artifact written to {args.output}")


if __name__ == "__main__":
    main()
