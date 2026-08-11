import random

from ai_core.calibration.selective_risk import (
    CalibrationRecord,
    select_calibrated_threshold,
)


def _make_records(n: int, seed: int, noise: float = 0.05) -> list[CalibrationRecord]:
    rng = random.Random(seed)
    records = []
    for _ in range(n):
        true_conf = rng.random()
        p_correct = 0.5 + 0.5 * true_conf
        correct = rng.random() < p_correct
        reported_conf = min(1.0, max(0.0, true_conf + rng.gauss(0, noise)))
        records.append(CalibrationRecord(confidence=reported_conf, correct=correct))
    return records


def test_too_small_calibration_set_falls_back_safely():
    records = _make_records(n=10, seed=1)
    outcome = select_calibrated_threshold(
        records, target_risk=0.10, delta=0.05, min_calibration_size=30
    )
    assert outcome.fallback_used is True
    assert outcome.calibration_set_size == 10
    # Fallback direction must be "escalate everything", never
    # "accept everything" — a broken/underpowered calibration must never
    # silently suppress escalations.
    assert outcome.coverage == 0.0


def test_unreachable_target_risk_falls_back_safely():
    # A wide, noisy confidence-correctness relationship with a very strict
    # target risk should be infeasible at this sample size, and must fall
    # back rather than emit a threshold that doesn't actually satisfy the
    # requested guarantee.
    records = _make_records(n=300, seed=2, noise=0.15)
    outcome = select_calibrated_threshold(
        records, target_risk=0.01, delta=0.05, min_calibration_size=30
    )
    assert outcome.fallback_used is True


def test_feasible_target_risk_yields_a_real_threshold_and_the_guarantee_holds():
    # Deterministic two-cluster construction (no reliance on random-seed
    # luck): a high-confidence cluster with a low error rate, and a
    # low-confidence cluster with a high error rate. The Hoeffding bound
    # at n=500 costs roughly sqrt(ln(1/0.05) / 1000) ~= 0.055, so a 5%
    # true error rate needs a target risk of at least ~0.11 to be
    # certifiable — target_risk=0.15 below gives comfortable headroom.
    high_conf_correct = [CalibrationRecord(confidence=0.9, correct=True) for _ in range(475)]
    high_conf_wrong = [CalibrationRecord(confidence=0.9, correct=False) for _ in range(25)]
    low_conf_correct = [CalibrationRecord(confidence=0.1, correct=True) for _ in range(200)]
    low_conf_wrong = [CalibrationRecord(confidence=0.1, correct=False) for _ in range(300)]
    records = high_conf_correct + high_conf_wrong + low_conf_correct + low_conf_wrong

    outcome = select_calibrated_threshold(
        records, target_risk=0.15, delta=0.05, min_calibration_size=30
    )
    assert outcome.fallback_used is False
    assert outcome.threshold >= 0.9
    assert outcome.coverage == 0.5  # only the high-confidence cluster is accepted
    assert outcome.risk_upper_bound_at_threshold <= outcome.target_risk

    # The core guarantee, checked directly: empirical risk among the
    # accepted (non-escalated) subset should not exceed the target risk.
    accepted = [r for r in records if r.confidence >= outcome.threshold]
    assert len(accepted) == outcome.n_accepted_at_threshold
    actual_risk = sum(1 for r in accepted if not r.correct) / len(accepted)
    assert actual_risk <= outcome.target_risk


def test_lower_target_risk_never_yields_higher_coverage_than_looser_target():
    # Monotonicity sanity check: asking for a stricter (lower) risk bound
    # should never result in MORE coverage than a looser bound, on the
    # same calibration set.
    records = _make_records(n=400, seed=11, noise=0.05)
    strict = select_calibrated_threshold(records, target_risk=0.10, delta=0.05)
    loose = select_calibrated_threshold(records, target_risk=0.30, delta=0.05)

    if not strict.fallback_used and not loose.fallback_used:
        assert strict.coverage <= loose.coverage


def test_perfectly_separable_confidence_finds_exact_threshold():
    # Construct a case where confidence perfectly predicts correctness:
    # everything with confidence >= 0.5 is correct, everything below is
    # wrong. With n=60 per side, the Hoeffding term alone is
    # sqrt(ln(20)/120) ~= 0.158, so target_risk must clear that even
    # though the true empirical risk in the accepted set is 0 — this is
    # the conservatism of Hoeffding at modest n, not a bug (see the
    # module docstring in selective_risk.py).
    records = [CalibrationRecord(confidence=0.9, correct=True) for _ in range(60)]
    records += [CalibrationRecord(confidence=0.1, correct=False) for _ in range(60)]

    outcome = select_calibrated_threshold(
        records, target_risk=0.20, delta=0.05, min_calibration_size=30
    )
    assert outcome.fallback_used is False
    assert outcome.threshold >= 0.5
    assert outcome.empirical_risk_at_threshold == 0.0
    assert outcome.coverage == 0.5
