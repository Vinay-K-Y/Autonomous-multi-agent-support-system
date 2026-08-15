"""Heuristic auto-labeling for NON-escalated outcomes: if the same
customer/conversation sends another message with a similar intent
within REOPEN_WINDOW_HOURS of a non-escalated response, treat the
earlier decision as incorrect (should have escalated). If enough time
has passed with no follow-up, treat it as correct (resolved without a
human).

This is a heuristic, not ground truth — document it as such wherever
these numbers get reported. Run periodically (e.g. daily cron).
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta

from ai_core.calibration.outcome_store import load_all_outcomes, mark_outcome

REOPEN_WINDOW_HOURS = 48


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reopen-window-hours", type=int, default=REOPEN_WINDOW_HOURS)
    args = parser.parse_args()

    outcomes = load_all_outcomes()
    unlabeled_non_escalated = [
        o for o in outcomes if not o.was_escalated and o.outcome_correct is None
    ]

    cutoff = datetime.now(UTC) - timedelta(hours=args.reopen_window_hours)

    for outcome in unlabeled_non_escalated:
        logged_at = datetime.fromisoformat(outcome.logged_at)
        if logged_at > cutoff:
            continue  # still within the reopen window, don't label yet

        # TODO: replace this with a real reopen check against
        # conversation history for this request's conversation_id.
        # Placeholder: assume no reopen was detected (label True).
        # Wire this to whatever conversation-history lookup exists in
        # ai_core/memory/ before relying on this in a real report.
        reopened = False

        mark_outcome(request_id=outcome.request_id, outcome_correct=not reopened)


if __name__ == "__main__":
    main()
