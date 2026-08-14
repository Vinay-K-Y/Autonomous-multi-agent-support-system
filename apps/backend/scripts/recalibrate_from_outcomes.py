"""Recompute the calibrated escalation threshold from a sliding window of
REAL production outcomes (not the one-off labeled dataset used by
scripts/compute_calibrated_threshold.py) — this is what turns calibration
from a one-time offline step into a self-tuning policy that adapts as the
classifier's real-world behavior drifts.

This reuses the exact same statistical method as the one-off pipeline
(select_calibrated_threshold, ai_core/calibration/selective_risk.py) — no
new statistics here, just a different, continuously-refreshed data
source: ai_core/calibration/data/outcome_log.jsonl, populated by
log_outcome() at request time and mark_outcome() once ground truth is
known (see ai_core/calibration/outcome_store.py and
ADAPTIVE_THRESHOLDS.md for how outcomes get labeled).

Run this periodically (e.g. a daily cron job, or triggered manually
after a batch of outcomes gets labeled) to keep the threshold current.

Usage:
    python scripts/recalibrate_from_outcomes.py --window-size 500
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime

from ai_core.calibration.models import CalibrationArtifact
from ai_core.calibration.outcome_store import load_labeled_outcomes_window
from ai_core.calibration.selective_risk import select_calibrated_threshold
from ai_core.calibration.store import DEFAULT_ARTIFACT_PATH, save_calibration_artifact
from app.core.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--window-size",
        type=int,
        default=500,
        help="Use at most this many of the most recently labeled outcomes.",
    )
    parser.add_argument("--target-risk", type=float, default=settings.CALIBRATION_TARGET_RISK)
    parser.add_argument("--delta", type=float, default=settings.CALIBRATION_DELTA)
    parser.add_argument("--min-calibration-size", type=int, default=30)
    parser.add_argument("--output", default=str(DEFAULT_ARTIFACT_PATH))
    args = parser.parse_args()

    outcomes = load_labeled_outcomes_window(window_size=args.window_size)
    if not outcomes:
        print(
            "No labeled outcomes found in ai_core/calibration/data/outcome_log.jsonl. "
            "Nothing to recalibrate — see ADAPTIVE_THRESHOLDS.md for how to log and "
            "label real production outcomes."
        )
        return

    records = [o.to_calibration_record() for o in outcomes]

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
        source_dataset=f"outcome_log.jsonl (sliding window, n={len(outcomes)})",
    )

    save_calibration_artifact(artifact, args.output)

    print(f"Recalibrated from {len(outcomes)} labeled production outcomes.")
    if artifact.fallback_used:
        print(f"FALLBACK: {artifact.fallback_reason}")
    else:
        print(f"New calibrated threshold: {artifact.threshold:.4f} "
              f"(coverage={artifact.coverage:.2%}, "
              f"risk_bound={artifact.risk_upper_bound_at_threshold:.4f})")
    print(f"Artifact written to {args.output}")
    print(
        "\nNote: this OVERWRITES the live threshold artifact that "
        "DecisionEngine reads. Compare against the previous artifact "
        "before trusting a large jump — a sudden shift usually means "
        "either real classifier drift, or a labeling process problem "
        "worth checking first."
    )


if __name__ == "__main__":
    main()
