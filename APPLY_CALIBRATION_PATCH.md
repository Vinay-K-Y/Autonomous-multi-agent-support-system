# Applying the Calibrated Escalation Patch

This patch adds Selective Guaranteed Risk (SGR) calibrated escalation on
top of `feature/multi-agent-orchestrator` at commit `b7a89e1`
("fix: Complete remaining tasks 4 and 6"). If your branch has moved past
that commit, the patch may need a rebase — see Troubleshooting below.

## How to apply it

From your repo root, with `feature/multi-agent-orchestrator` checked out:

```bash
git checkout feature/multi-agent-orchestrator
git pull origin feature/multi-agent-orchestrator
git am 0001-calibrated-escalation.patch
```

`git am` (not `git apply`) preserves the original commit message and
authorship — use it, not a plain patch apply, so the history stays clean.

If `git am` fails because your branch has diverged from `b7a89e1`, fall
back to:

```bash
git apply --reject 0001-calibrated-escalation.patch
```
This applies whatever hunks still match cleanly and writes `.rej` files
for any that don't — check those manually, they'll be small (the patch
only touches `decision_engine.py`, `config.py`, and `env.example` as
modifications; everything else is new files, which always apply cleanly
regardless of drift).

## What's in it

16 files, all new except three modified: `decision_engine.py`,
`config.py`, `env.example`. Full breakdown is in the commit message
(`git log -1` after applying) and in `CALIBRATION.md`, which the patch
adds to the repo root of `apps/backend/`.

## Verify it worked

```bash
cd apps/backend
pip install -e . --break-system-packages   # if not already installed
PYTHONPATH=. python -m pytest tests/test_selective_risk.py tests/test_decision_engine_calibration.py tests/test_decision_engine_behavior.py tests/test_decision_engine.py -v
```

All 17 tests should pass (5 new algorithm tests, 4 new integration
tests, 8 pre-existing decision-engine tests — unchanged, proving zero
regression).

## Important: this ships inert by default

No `ai_core/calibration/data/calibrated_thresholds.json` is included —
only a clearly-labeled `demo_calibrated_thresholds.json`. This means
`DecisionEngine` will use the exact same static `ESCALATION_THRESHOLD`
(0.7) as before until you deliberately run the real calibration
pipeline. Read `CALIBRATION.md` for the two-script flow
(`collect_calibration_data.py` needs your live LLM credentials;
`compute_calibrated_threshold.py` is pure statistics, no network).

## Ask your IDE agent to do next, if you want to go further

1. Extend `ai_core/calibration/data/labeled_examples.jsonl` (currently
   42 synthetic seed examples) with real, representative support
   messages and their true intents.
2. Run `collect_calibration_data.py` against your real LLM setup.
3. Run `compute_calibrated_threshold.py` and inspect the resulting
   `calibrated_thresholds.json` — check whether it's a real threshold
   or a fallback (if fallback, you likely need more labeled data or a
   looser `--target-risk`).
4. For the empirical study that turns this into an actual novelty
   claim (see the last section of `CALIBRATION.md`): hold out a test
   set separate from the calibration set, and report whether the true
   error rate on the held-out set actually respects the guarantee.
