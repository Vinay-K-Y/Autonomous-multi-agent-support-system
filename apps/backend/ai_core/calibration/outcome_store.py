from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from ai_core.calibration.models import OutcomeRecord
from ai_core.calibration.store import DATA_DIR

DEFAULT_OUTCOME_LOG_PATH = DATA_DIR / "outcome_log.jsonl"


def log_outcome(
    request_id: str,
    confidence: float,
    threshold_used: float,
    was_escalated: bool,
    path: Optional[Path] = None,
) -> OutcomeRecord:
    """Called at request-handling time (not yet knowing the outcome) to
    record what decision was made and under what confidence/threshold.
    outcome_correct starts as None — see mark_outcome() to fill it in
    once ground truth is available."""
    record = OutcomeRecord(
        request_id=request_id,
        confidence=confidence,
        threshold_used=threshold_used,
        was_escalated=was_escalated,
        outcome_correct=None,
        logged_at=datetime.now(UTC).isoformat(),
    )
    path = path or DEFAULT_OUTCOME_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(record.model_dump_json() + "\n")
    return record


def mark_outcome(
    request_id: str,
    outcome_correct: bool,
    path: Optional[Path] = None,
) -> bool:
    """Fill in the ground-truth label for a previously logged outcome.

    This rewrites the whole log file (simple, correct, and fine at the
    data volumes a college-project-scale support system will see; if this
    becomes a real bottleneck, swap to a proper outcome table in the
    existing Postgres database instead of a flat file — see
    ADAPTIVE_THRESHOLDS.md).

    Returns True if a matching un-labeled record was found and updated,
    False otherwise (already labeled, or request_id not found).
    """
    path = path or DEFAULT_OUTCOME_LOG_PATH
    if not path.exists():
        return False

    records = load_all_outcomes(path)
    found = False
    updated_records: list[OutcomeRecord] = []
    for record in records:
        if record.request_id == request_id and record.outcome_correct is None:
            record = record.model_copy(
                update={
                    "outcome_correct": outcome_correct,
                    "labeled_at": datetime.now(UTC).isoformat(),
                }
            )
            found = True
        updated_records.append(record)

    if not found:
        return False

    with path.open("w") as f:
        for record in updated_records:
            f.write(record.model_dump_json() + "\n")
    return True


def load_all_outcomes(path: Optional[Path] = None) -> list[OutcomeRecord]:
    path = path or DEFAULT_OUTCOME_LOG_PATH
    if not path.exists():
        return []
    records = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(OutcomeRecord.model_validate_json(line))
    return records


def load_labeled_outcomes_window(
    window_size: Optional[int] = None,
    path: Optional[Path] = None,
) -> list[OutcomeRecord]:
    """Load labeled (outcome_correct is not None) outcomes, most recent
    first, optionally limited to the last `window_size` — this is the
    sliding-window feedback set that scripts/recalibrate_from_outcomes.py
    feeds into select_calibrated_threshold()."""
    all_records = load_all_outcomes(path)
    labeled = [r for r in all_records if r.outcome_correct is not None]
    labeled.sort(key=lambda r: r.labeled_at or "", reverse=True)
    if window_size is not None:
        labeled = labeled[:window_size]
    return labeled
