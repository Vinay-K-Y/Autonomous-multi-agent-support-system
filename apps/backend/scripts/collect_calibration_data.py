"""Collect calibration data by running the REAL IntentAgent (real LLM
calls, using whatever LLM_PROVIDER is configured in .env) against a
labeled dataset of (message, true_intent) pairs.

This is the one step in the calibration pipeline that costs real LLM
calls and needs network access / API credentials. Run it once (or
periodically, as your labeled set grows) to produce
calibration_examples.jsonl, then run compute_calibrated_threshold.py
(no network needed) to turn that into a threshold artifact.

Usage:
    python scripts/collect_calibration_data.py \
        --labeled-data ai_core/calibration/data/labeled_examples.jsonl \
        --output ai_core/calibration/data/calibration_examples.jsonl

--labeled-data must be a .jsonl file where each line is:
    {"message": "I want a refund for my broken headphones", "true_intent": "refund"}

true_intent must be one of the ai_core.models.intent.IntentType values:
refund, technical_issue, billing_issue, delivery_issue, account_issue,
general_query, other.

The more labeled examples you provide (and the more representative they
are of real production traffic), the tighter the resulting calibrated
threshold's guarantee will be — see CALIBRATION.md.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from ai_core.agents.intent_agent import IntentAgent
from ai_core.calibration.models import CalibrationExample
from ai_core.calibration.store import save_calibration_examples
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState


async def collect(labeled_path: Path, output_path: Path) -> None:
    agent = IntentAgent()

    with labeled_path.open() as f:
        labeled = [json.loads(line) for line in f if line.strip()]

    results: list[CalibrationExample] = []

    for i, item in enumerate(labeled, start=1):
        message = item["message"]
        true_intent = item["true_intent"]

        state = SupportState(
            request=CustomerRequest(message=message),
            metadata=ProcessingMetadata(request_id=f"calibration-{i}"),
        )
        state = await agent.execute(state)

        predicted_intent = state.intent.intent.value
        confidence = state.intent.confidence

        results.append(
            CalibrationExample(
                message=message,
                true_intent=true_intent,
                predicted_intent=predicted_intent,
                confidence=confidence,
            )
        )
        match = "OK" if predicted_intent == true_intent else "MISS"
        print(
            f"[{i}/{len(labeled)}] {match} predicted={predicted_intent} "
            f"true={true_intent} confidence={confidence:.3f}"
        )

    save_calibration_examples(results, output_path)
    print(f"\nWrote {len(results)} calibration examples to {output_path}")
    n_correct = sum(1 for r in results if r.correct)
    print(f"Raw accuracy on this labeled set: {n_correct}/{len(results)} "
          f"({n_correct / len(results):.1%}) — this is NOT the calibrated "
          "guarantee, just a sanity check. Run compute_calibrated_threshold.py "
          "for the actual guaranteed threshold.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labeled-data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(collect(args.labeled_data, args.output))


if __name__ == "__main__":
    main()
