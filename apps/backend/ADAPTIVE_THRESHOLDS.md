# Adaptive (Outcome-Driven) Escalation Thresholds

## What this adds on top of CALIBRATION.md

`CALIBRATION.md` describes a one-time calibration: label some examples,
run them through the real classifier once, compute a threshold, done.
That threshold is only as good as the moment it was computed — if the
classifier's real-world behavior drifts (model update, new kinds of
support queries, prompt changes), the threshold goes stale and nobody
notices.

This feature turns that one-off pipeline into a continuously-refreshed
one, fed by real production outcomes instead of a static labeled
dataset — a simple, honest version of "self-tuning."

**Important scoping note:** this is a sliding-window re-application of
the same SGR statistics from #1, triggered periodically — not a
contextual bandit or reinforcement-learning policy. A full bandit
formulation (treating threshold choice as an action with a reward
signal, balancing exploration/exploitation) is a legitimate future
extension, but isn't what's implemented here; be precise about that
distinction if this goes into a report, since overclaiming "bandit
algorithm" for what's actually a periodic batch recomputation would be
an easy thing for a reviewer to catch.

## Architecture

```
Every real request:
  DecisionEngine.evaluate() records escalation_threshold_used on DecisionResult
        |
        v
  support_service.py calls log_outcome(request_id, confidence,
                                        threshold_used, was_escalated)
        |
        v
  ai_core/calibration/data/outcome_log.jsonl   <- grows continuously,
                                                   outcome_correct=None
                                                   for every new record

Later, once ground truth is known:
  POST /api/v1/feedback/escalation-outcome  {request_id, outcome_correct}
        |
        v
  mark_outcome() finds the matching record and labels it
        |
        v
  outcome_log.jsonl now has outcome_correct=True/False for that record

Periodically (cron, or triggered manually):
  scripts/recalibrate_from_outcomes.py
        |
        v
  loads the N most recently LABELED outcomes (sliding window)
        |
        v
  select_calibrated_threshold()  <- the exact same SGR algorithm from #1
        |
        v
  overwrites ai_core/calibration/data/calibrated_thresholds.json
        |
        v
  DecisionEngine picks up the new threshold on next process start
  (or CalibratedThresholdProvider.reload())
```

## Where ground truth actually comes from

This is the part that has to be connected to something real — the code
here builds the mechanism, but "was this escalation actually necessary"
is a judgment call that has to come from somewhere:

- **Escalated requests**: whoever handles the human-review queue marks
  whether the request genuinely needed a person, vs. something the
  system could have resolved on its own. This would naturally hook into
  wherever human review completion happens (there's no such endpoint
  yet in this codebase — `human_review_tool.py` only creates the
  `HumanReview` record, it doesn't have a resolution/completion step).
- **Non-escalated requests**: harder, because by definition no human
  looked at them. A reasonable proxy: did the conversation reopen, or
  did the customer ask again / complain, within some follow-up window?
  That requires wiring into `conversation_manager` / ticket
  reopen-tracking, which also doesn't exist yet.

Both of these are real, unbuilt integration points — this feature ships
the statistics and the plumbing (logging, labeling, recalibration), not
a synthetic answer to "how do you know if a decision was right." Be
upfront about this if presenting the feature: what's genuinely built is
"the system can learn from labeled outcomes once they exist," not "the
system generates its own ground truth."

## Running it

1. Real requests accumulate in `outcome_log.jsonl` automatically once
   this patch is applied — no action needed, `support_service.py` logs
   every decision.

2. Label some of them (manually, via a script, or via the feedback
   endpoint once you've built the real completion/reopen hooks above):
   ```
   curl -X POST http://localhost:8000/api/v1/feedback/escalation-outcome \
     -H "Content-Type: application/json" \
     -d '{"request_id": "abc-123", "outcome_correct": true}'
   ```

3. Recalibrate from the labeled subset:
   ```
   python scripts/recalibrate_from_outcomes.py --window-size 500
   ```
   This is pure statistics again (no network needed) — same as
   `compute_calibrated_threshold.py`, just reading from
   `outcome_log.jsonl` instead of a one-off `calibration_examples.jsonl`.

## Honest limitation carried over from #1

The Hoeffding bound's sample-size requirement (see CALIBRATION.md)
applies here too — if you only have a few dozen labeled outcomes in the
sliding window, recalibration will likely fall back to the static
threshold, same as the one-off pipeline did initially. This is correct,
conservative behavior, not a bug: an adaptive policy with too little
feedback to trust shouldn't pretend otherwise.

## What would make this a stronger empirical result

Track the threshold artifact's `computed_at` and `threshold` over
several recalibration runs and plot it over time. If it's genuinely
adapting to something real (classifier drift, seasonal query mix
changes), you'd expect to see it move meaningfully between runs as more
outcomes accumulate — and you can report *how much* labeled feedback it
took before recalibration stopped falling back and started producing a
real threshold. That's a concrete, measurable claim about the sample
efficiency of the adaptive layer, not just "we built a mechanism."
