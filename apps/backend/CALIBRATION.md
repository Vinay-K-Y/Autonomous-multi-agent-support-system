# Calibrated Escalation

## What this replaces

Before this feature, `DecisionEngine.should_escalate()` compared the
intent classifier's self-reported confidence against a single hand-picked
number, `ESCALATION_THRESHOLD = 0.7` (`app/core/config.py`). That number
has no statistical grounding — it's a guess, and LLM-reported confidence
scores are known to be poorly calibrated (a model saying "0.9" doesn't
reliably mean it's right 90% of the time).

This feature replaces that guess with a threshold computed from labeled
data, using a method that gives an actual statistical guarantee:

> "Requests that are NOT escalated will be wrong at most `target_risk`
> fraction of the time, with probability at least `1 - delta`."

## Method: Selective Guaranteed Risk (SGR)

Implemented in `ai_core/calibration/selective_risk.py`, following:

> Geifman, Y. & El-Yaniv, R. (2017). "Selective Classification for Deep
> Neural Networks." NeurIPS 2017.

Given a calibration set of `(confidence, was_correct)` pairs, SGR finds
the *lowest* confidence threshold `tau` such that the empirical error
rate among predictions with `confidence >= tau`, plus a concentration
bound, stays under `target_risk`. Lower `tau` means higher coverage
(fewer things get escalated), so SGR picks the most permissive threshold
that still satisfies the guarantee.

We use a **Hoeffding bound** for the concentration term (not the tighter
Clopper-Pearson exact binomial bound) because it needs no numerical
dependencies beyond the Python standard library. It's more conservative
— you'll need more calibration data to certify a given risk level than
you would with Clopper-Pearson — but it's simple to audit and there are
no new dependencies to add to `pyproject.toml`. See the module docstring
for the exact bound formula and where to swap in a tighter one later.

**Important honesty note about sample size:** the Hoeffding term costs
roughly `sqrt(ln(1/delta) / (2n))` on its own. At `n=100`, `delta=0.05`,
that's already ~0.12 — meaning you can't certify a target risk below
~0.12 no matter how good your classifier is, until you have more
calibration data. This is expected behavior, not a bug: when no
threshold can satisfy the target risk, the system **falls back to
escalating everything** rather than emitting an ungrounded number. It
never fails in the direction of under-escalating.

## Architecture: how it plugs into the existing pipeline

```
labeled_examples.jsonl  (you write this: message + true_intent)
        |
        v  scripts/collect_calibration_data.py  (real LLM calls, needs network)
calibration_examples.jsonl  (message, true_intent, predicted_intent, confidence)
        |
        v  scripts/compute_calibrated_threshold.py  (pure statistics, no network)
calibrated_thresholds.json  (the artifact — threshold + guarantee metadata)
        |
        v  CalibratedThresholdProvider (ai_core/calibration/provider.py)
        |
        v  DecisionEngine.should_escalate()  (ai_core/workflow/decision_engine.py)
```

`DecisionEngine` doesn't know or care whether the threshold it's using is
calibrated or static — it just calls
`self.threshold_provider.get_escalation_threshold()`, which:

- returns the calibrated threshold if `ai_core/calibration/data/calibrated_thresholds.json`
  exists **and** its own calibration run didn't fall back, otherwise
- returns `settings.ESCALATION_THRESHOLD` (the original static value)

This means: **the repository ships with unchanged behavior by default.**
No `calibrated_thresholds.json` exists at that path out of the box (only
a clearly-labeled `demo_calibrated_thresholds.json` does, for
demonstration — see below). Every pre-existing decision-engine test
still passes untouched.

## Running it for real

1. **Label examples.** Extend `ai_core/calibration/data/labeled_examples.jsonl`
   (42 synthetic seed examples are provided across all 7 intent types —
   replace/extend these with real, representative support messages and
   their true intents; more and more-representative data gives a tighter
   guarantee).

2. **Collect predictions** (needs a working LLM provider configured via `.env`,
   same as the rest of the app):
   ```
   python scripts/collect_calibration_data.py \
       --labeled-data ai_core/calibration/data/labeled_examples.jsonl \
       --output ai_core/calibration/data/calibration_examples.jsonl
   ```

3. **Compute the calibrated threshold** (pure statistics, no network needed):
   ```
   python scripts/compute_calibrated_threshold.py \
       --examples ai_core/calibration/data/calibration_examples.jsonl \
       --target-risk 0.10 \
       --delta 0.05
   ```
   This writes `ai_core/calibration/data/calibrated_thresholds.json`,
   which `DecisionEngine` picks up automatically on next process start
   (or call `calibrated_threshold_provider.reload()` to pick it up live).

## What's real vs. demo in this repo right now

- `ai_core/calibration/data/labeled_examples.jsonl` — **real, usable**
  seed data (42 examples across all 7 intents). Extend it and run
  `collect_calibration_data.py` against your own LLM setup to get real
  calibration data.
- `ai_core/calibration/data/demo_calibration_examples.jsonl` and
  `demo_calibrated_thresholds.json` — **synthetic demonstration data**
  showing the statistics pipeline works end-to-end (a simulated
  classifier with confidence correlated to correctness), NOT real model
  output. Do not use these for production decisions — they exist so the
  pipeline is provably exercised without requiring live API credentials
  to reproduce.

## Suggested empirical study (this is the actual novelty claim)

The calibration mechanism on its own is an implementation of an existing
method (SGR), applied to a workflow-orchestration context it doesn't
appear to have been applied to before, as far as the surrounding
literature review for this project found. The stronger, more citable
claim is empirical: run `collect_calibration_data.py` against a real
labeled dataset of a few hundred examples, then report:

- the calibrated threshold vs. the hand-picked 0.7 default,
- the coverage (fraction not escalated) at a couple of different
  `target_risk` levels,
- and — most importantly — whether the *actual* error rate on a held-out
  test set (not the calibration set itself) matches the guarantee.

That comparison is what turns "we added a formula" into a real result.
