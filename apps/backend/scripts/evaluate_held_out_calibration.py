"""Given a calibrated threshold artifact and REAL predictions on a
held-out set the threshold was NOT computed from, check whether the
guarantee actually holds. This is the step that turns "we implemented
SGR" into "we validated it."

Usage:
    python scripts/evaluate_held_out_calibration.py \
        --holdout-examples ai_core/calibration/data/holdout_calibration_examples.jsonl \
        --artifact ai_core/calibration/data/calibrated_thresholds.json
"""
import argparse
import json
from pathlib import Path

from ai_core.calibration.store import load_calibration_artifact, load_calibration_examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout-examples", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()

    artifact = load_calibration_artifact(args.artifact)
    if artifact is None:
        raise SystemExit(f"No artifact found at {args.artifact}")
    if artifact.fallback_used:
        raise SystemExit(
            "Artifact used the fallback (escalate everything) — there is no "
            "non-trivial threshold to validate against held-out data."
        )

    examples = load_calibration_examples(args.holdout_examples)
    accepted = [e for e in examples if e.confidence >= artifact.threshold]

    if not accepted:
        print(f"No held-out examples cleared the threshold ({artifact.threshold:.4f}); "
              f"cannot evaluate on this split.")
        return

    n_correct = sum(1 for e in accepted if e.correct)
    actual_risk = 1 - (n_correct / len(accepted))

    print(f"Threshold: {artifact.threshold:.4f}")
    print(f"Held-out accepted set size: {len(accepted)} / {len(examples)}")
    print(f"Held-out empirical risk: {actual_risk:.4f}")
    print(f"Target risk (from artifact): {artifact.target_risk:.4f}")
    print(f"Guarantee held on held-out data: {actual_risk <= artifact.target_risk}")
    if actual_risk > artifact.target_risk:
        print(
            "\nWARNING: the guarantee did NOT hold on held-out data. This can "
            "happen by chance (the Hoeffding bound is probabilistic, not "
            "absolute — it should hold with probability >= 1-delta, not 100% "
            "of the time), but if it fails repeatedly across multiple holdout "
            "splits, something is wrong (e.g. calibration and production data "
            "aren't actually from the same distribution)."
        )


if __name__ == "__main__":
    main()
