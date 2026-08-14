from pathlib import Path

from ai_core.calibration.outcome_store import (
    load_all_outcomes,
    load_labeled_outcomes_window,
    log_outcome,
    mark_outcome,
)


def test_log_outcome_writes_unlabeled_record(tmp_path: Path):
    path = tmp_path / "outcome_log.jsonl"
    record = log_outcome(
        request_id="REQ-1",
        confidence=0.65,
        threshold_used=0.7,
        was_escalated=True,
        path=path,
    )
    assert record.outcome_correct is None
    assert record.labeled_at is None

    all_records = load_all_outcomes(path)
    assert len(all_records) == 1
    assert all_records[0].request_id == "REQ-1"


def test_mark_outcome_labels_the_matching_record(tmp_path: Path):
    path = tmp_path / "outcome_log.jsonl"
    log_outcome(request_id="REQ-1", confidence=0.65, threshold_used=0.7, was_escalated=True, path=path)
    log_outcome(request_id="REQ-2", confidence=0.9, threshold_used=0.7, was_escalated=False, path=path)

    found = mark_outcome(request_id="REQ-1", outcome_correct=True, path=path)
    assert found is True

    all_records = load_all_outcomes(path)
    req1 = next(r for r in all_records if r.request_id == "REQ-1")
    req2 = next(r for r in all_records if r.request_id == "REQ-2")

    assert req1.outcome_correct is True
    assert req1.labeled_at is not None
    # REQ-2 must be untouched.
    assert req2.outcome_correct is None


def test_mark_outcome_returns_false_for_unknown_request_id(tmp_path: Path):
    path = tmp_path / "outcome_log.jsonl"
    log_outcome(request_id="REQ-1", confidence=0.65, threshold_used=0.7, was_escalated=True, path=path)

    found = mark_outcome(request_id="DOES-NOT-EXIST", outcome_correct=True, path=path)
    assert found is False


def test_mark_outcome_returns_false_if_already_labeled(tmp_path: Path):
    path = tmp_path / "outcome_log.jsonl"
    log_outcome(request_id="REQ-1", confidence=0.65, threshold_used=0.7, was_escalated=True, path=path)

    first = mark_outcome(request_id="REQ-1", outcome_correct=True, path=path)
    second = mark_outcome(request_id="REQ-1", outcome_correct=False, path=path)

    assert first is True
    assert second is False  # already labeled — must not silently overwrite

    all_records = load_all_outcomes(path)
    assert all_records[0].outcome_correct is True  # unchanged from the first label


def test_load_labeled_outcomes_window_excludes_unlabeled_and_respects_window_size(tmp_path: Path):
    path = tmp_path / "outcome_log.jsonl"
    for i in range(5):
        log_outcome(request_id=f"REQ-{i}", confidence=0.7, threshold_used=0.7, was_escalated=False, path=path)

    # Label only 3 of the 5.
    for i in range(3):
        mark_outcome(request_id=f"REQ-{i}", outcome_correct=True, path=path)

    all_labeled = load_labeled_outcomes_window(path=path)
    assert len(all_labeled) == 3
    assert all(r.outcome_correct is not None for r in all_labeled)

    windowed = load_labeled_outcomes_window(window_size=2, path=path)
    assert len(windowed) == 2


def test_load_all_outcomes_on_missing_file_returns_empty_list(tmp_path: Path):
    path = tmp_path / "does_not_exist.jsonl"
    assert load_all_outcomes(path) == []
    assert load_labeled_outcomes_window(path=path) == []
