"""Split labeled_examples.jsonl into calibration and held-out sets,
stratified roughly by intent so both splits cover all 7 intent types.

Usage:
    python scripts/split_labeled_data.py \
        --input ai_core/calibration/data/labeled_examples.jsonl \
        --calibration-output ai_core/calibration/data/labeled_calibration_split.jsonl \
        --holdout-output ai_core/calibration/data/labeled_holdout_split.jsonl \
        --holdout-fraction 0.3 \
        --seed 42
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--calibration-output", type=Path, required=True)
    parser.add_argument("--holdout-output", type=Path, required=True)
    parser.add_argument("--holdout-fraction", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rows = [json.loads(l) for l in args.input.open() if l.strip()]

    by_intent = defaultdict(list)
    for row in rows:
        by_intent[row["true_intent"]].append(row)

    calibration, holdout = [], []
    for intent, group in by_intent.items():
        rng.shuffle(group)
        n_holdout = max(1, int(len(group) * args.holdout_fraction))
        holdout.extend(group[:n_holdout])
        calibration.extend(group[n_holdout:])

    for path, data in [(args.calibration_output, calibration), (args.holdout_output, holdout)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            for row in data:
                f.write(json.dumps(row) + "\n")

    print(f"Calibration set: {len(calibration)} examples -> {args.calibration_output}")
    print(f"Holdout set: {len(holdout)} examples -> {args.holdout_output}")


if __name__ == "__main__":
    main()
