# Applying the Routing Benchmark + Adaptive Thresholds Patch

This patch is built on top of the calibrated escalation patch
(`0001-calibrated-escalation.patch`, commit `0516f51`), which must be
applied first. It commits on top of your current branch tip at `8cc4ad6`
("Add real calibration data and infrastructure").

## How to apply it

```bash
git checkout feature/multi-agent-orchestrator
git pull origin feature/multi-agent-orchestrator
git am 0002-routing-benchmark-and-adaptive-thresholds.patch
```

Same guidance as before: use `git am`, not `git apply`, to preserve the
commit message. If your branch has diverged, fall back to
`git apply --reject` and manually resolve any `.rej` files — the only
modified (not new) files in this patch are:
`ai_core/calibration/models.py`, `ai_core/graph/builder.py`,
`ai_core/models/decision.py`, `ai_core/state/support_state.py`,
`ai_core/workflow/decision_engine.py`, `app/main.py`,
`app/mappers/support_mapper.py`, `app/schemas/response.py`,
`app/services/support_service.py` — everything else is a new file and
will apply cleanly regardless.

## Verify it worked

```bash
cd apps/backend
PYTHONPATH=. python -m pytest \
  tests/test_selective_risk.py \
  tests/test_decision_engine_calibration.py \
  tests/test_decision_engine_behavior.py \
  tests/test_decision_engine.py \
  tests/test_outcome_store.py \
  tests/test_benchmark_conditional_routing.py \
  tests/test_support_mapper.py \
  -v
```
28 tests should pass.

**One test is NOT covered above and needs your full dependency
environment to run**: `tests/test_conditional_routing.py`. It requires
importing `ai_core.graph.builder`, which pulls in the full
LangChain/LangGraph chain — I could not install that dependency tree in
my sandbox (repeated timeouts on `langchain-google-genai`). Run it
specifically once your environment is set up:
```bash
PYTHONPATH=. python -m pytest tests/test_conditional_routing.py -v
```
I traced the underlying 4-line change (an early-return in
`route_after_intent` for `state.force_full_pipeline`) by hand and I'm
confident in it, but it's the one thing in this patch I did not verify
by actually running it — worth confirming first.

## What's in it — two independent features

**Conditional-routing benchmark** (`ai_core/benchmarks/`,
`scripts/benchmark_conditional_routing.py`): run it once your `.env` LLM
provider is configured:
```bash
python scripts/benchmark_conditional_routing.py
```
This needs real network/LLM calls — there's no offline mode, since the
entire point is measuring real latency and call counts. It writes a
results JSON with p50/p95 latency and call-count comparisons between
adaptive routing and always-full-pipeline, plus flags any query where
the two configurations disagree on predicted intent.

**Outcome-driven adaptive thresholds** (`ai_core/calibration/outcome_store.py`,
`scripts/recalibrate_from_outcomes.py`, `app/routers/feedback.py`): this
one ships **inert but wired** — `support_service.py` will start logging
an outcome record for every real request immediately after you apply
this patch (fails safe, never breaks a live request). But nothing acts
on those logs until you label some via the new
`POST /api/v1/feedback/escalation-outcome` endpoint and run
`scripts/recalibrate_from_outcomes.py`.

**Read `ADAPTIVE_THRESHOLDS.md` before presenting this feature anywhere** —
it's explicit that the ground-truth labeling step (was an escalation
actually necessary? did a non-escalated request get reopened?) isn't
built. This patch gives you the logging, labeling endpoint, and
recalibration statistics — not an automatic answer to "was the decision
right." That connection (to a real human-review completion flow or
ticket-reopen tracking) is real, unbuilt future work, and the doc says
so — don't let a summary of this feature imply otherwise.

## Suggested next steps, in order

1. Apply and run the test suite above.
2. Run `benchmark_conditional_routing.py` for real — this is fully
   self-contained and gives you an actual number (latency/cost
   reduction from adaptive routing) with no further plumbing needed.
3. Decide whether to build one of the two ground-truth capture hooks
   named in `ADAPTIVE_THRESHOLDS.md` (human-review completion or
   ticket-reopen tracking) — that's the one piece of real engineering
   work left before the adaptive-threshold feature can produce a result
   instead of just sitting ready.
