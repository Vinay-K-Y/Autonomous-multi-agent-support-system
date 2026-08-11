"""Selective Guaranteed Risk (SGR) threshold calibration.

Replaces a hand-picked confidence threshold (e.g. ``ESCALATION_THRESHOLD =
0.7``) with a threshold that carries a statistical guarantee, computed from
a held-out calibration set of (confidence, was_correct) pairs.

Method
------
This implements the Selective Guaranteed Risk procedure from:

    Geifman, Y. & El-Yaniv, R. (2017). "Selective Classification for Deep
    Neural Networks." NeurIPS 2017.

Given a target risk level ``alpha`` (e.g. "at most 5% of *accepted*
predictions should be wrong") and a confidence level ``1 - delta`` (e.g.
"we want this guarantee to hold with 95% probability over the randomness
of the calibration set"), the procedure finds the *lowest* confidence
threshold tau such that the empirical risk among predictions with
confidence >= tau, plus a Hoeffding concentration bound, does not exceed
alpha:

    r_hat(tau) + sqrt(ln(1/delta) / (2 * n(tau))) <= alpha

Choosing the lowest such tau maximizes coverage (fewest escalations)
subject to the risk guarantee. This is a distribution-free, finite-sample
guarantee — it does not assume the LLM's confidence scores are
well-calibrated in the usual probabilistic sense; it only assumes the
calibration set is drawn i.i.d. from the same distribution as production
traffic.

We use a Hoeffding bound rather than the tighter Clopper-Pearson exact
binomial bound because it requires no external numerical dependencies
(no scipy) and is simple to audit. It is more conservative (a larger n is
needed to reach a given coverage), which is an acceptable trade for a
first implementation — see CALIBRATION.md for how to swap in a tighter
bound later.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationRecord:
    """One labeled calibration example: what confidence the model reported,
    and whether its prediction was actually correct."""

    confidence: float
    correct: bool


@dataclass(frozen=True)
class CalibrationOutcome:
    """Result of running SGR threshold selection over a calibration set."""

    threshold: float
    target_risk: float
    delta: float
    calibration_set_size: int
    n_accepted_at_threshold: int
    empirical_risk_at_threshold: float
    risk_upper_bound_at_threshold: float
    coverage: float
    fallback_used: bool
    fallback_reason: str | None = None


def _hoeffding_upper_bound(risk_hat: float, n: int, delta: float) -> float:
    """One-sided Hoeffding upper confidence bound on a Bernoulli risk.

    P(true_risk <= risk_hat + bound) >= 1 - delta
    """
    if n <= 0:
        return 1.0
    return risk_hat + math.sqrt(math.log(1.0 / delta) / (2.0 * n))


def select_calibrated_threshold(
    records: list[CalibrationRecord],
    target_risk: float = 0.05,
    delta: float = 0.05,
    min_calibration_size: int = 30,
) -> CalibrationOutcome:
    """Select the lowest confidence threshold whose Hoeffding-bounded risk
    does not exceed ``target_risk``, with confidence ``1 - delta``.

    Falls back to "accept nothing below max confidence" (i.e. escalate
    everything) if the calibration set is too small or no threshold
    satisfies the risk bound — this is the safe direction to fail in, since
    it never under-escalates.
    """
    n = len(records)

    if n < min_calibration_size:
        max_conf = max((r.confidence for r in records), default=1.0)
        fallback_threshold = min(1.0, max_conf + 1e-6)
        return CalibrationOutcome(
            threshold=fallback_threshold,
            target_risk=target_risk,
            delta=delta,
            calibration_set_size=n,
            n_accepted_at_threshold=0,
            empirical_risk_at_threshold=0.0,
            risk_upper_bound_at_threshold=0.0,
            coverage=0.0,
            fallback_used=True,
            fallback_reason=(
                f"Calibration set has {n} records; need at least "
                f"{min_calibration_size} for a statistically meaningful "
                f"bound. Escalating everything until more labeled data "
                f"is collected."
            ),
        )

    candidate_thresholds = sorted({r.confidence for r in records})

    best: CalibrationOutcome | None = None

    for tau in candidate_thresholds:
        accepted = [r for r in records if r.confidence >= tau]
        n_accepted = len(accepted)
        if n_accepted == 0:
            continue

        n_incorrect = sum(1 for r in accepted if not r.correct)
        risk_hat = n_incorrect / n_accepted
        risk_ucb = _hoeffding_upper_bound(risk_hat, n_accepted, delta)

        if risk_ucb <= target_risk:
            candidate = CalibrationOutcome(
                threshold=tau,
                target_risk=target_risk,
                delta=delta,
                calibration_set_size=n,
                n_accepted_at_threshold=n_accepted,
                empirical_risk_at_threshold=risk_hat,
                risk_upper_bound_at_threshold=risk_ucb,
                coverage=n_accepted / n,
                fallback_used=False,
            )
            # Lower tau => higher coverage. Candidate thresholds are sorted
            # ascending, so the first feasible one has the highest coverage
            # among feasible thresholds found so far — keep scanning only
            # to find an even lower feasible tau (shouldn't exist given
            # monotonicity in expectation, but risk_hat is not strictly
            # monotone in finite samples, so we take the true minimum).
            if best is None or candidate.threshold < best.threshold:
                best = candidate

    if best is not None:
        return best

    max_conf = max(r.confidence for r in records)
    fallback_threshold = min(1.0, max_conf + 1e-6)
    return CalibrationOutcome(
        threshold=fallback_threshold,
        target_risk=target_risk,
        delta=delta,
        calibration_set_size=n,
        n_accepted_at_threshold=0,
        empirical_risk_at_threshold=0.0,
        risk_upper_bound_at_threshold=0.0,
        coverage=0.0,
        fallback_used=True,
        fallback_reason=(
            "No confidence threshold in the calibration set satisfies the "
            f"target risk {target_risk} at confidence level {1 - delta}. "
            "Escalating everything until the underlying intent classifier "
            "improves or more calibration data is collected."
        ),
    )
