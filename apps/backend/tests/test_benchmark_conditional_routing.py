import sys
from pathlib import Path

# scripts/ isn't a package; import the module directly by path so these
# tests don't need scripts/__init__.py or a packaging change.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from benchmark_conditional_routing import RunResult, _percentile, summarize  # noqa: E402


def test_percentile_matches_known_values():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert _percentile(values, 50) == 30.0
    assert _percentile(values, 0) == 10.0
    assert _percentile(values, 100) == 50.0


def test_percentile_empty_list_returns_zero():
    assert _percentile([], 50) == 0.0


def _run(message, config, latency_ms, llm_calls, intent, took_shortcut):
    return RunResult(
        message=message,
        query_type="high_confidence_general",
        config=config,
        latency_ms=latency_ms,
        llm_call_count=llm_calls,
        predicted_intent=intent,
        confidence=0.9,
        took_shortcut=took_shortcut,
    )


def test_summarize_computes_latency_and_call_reduction():
    results = [
        _run("q1", "adaptive", latency_ms=100, llm_calls=1, intent="general_query", took_shortcut=True),
        _run("q1", "full_pipeline", latency_ms=400, llm_calls=3, intent="general_query", took_shortcut=False),
        _run("q2", "adaptive", latency_ms=120, llm_calls=1, intent="general_query", took_shortcut=True),
        _run("q2", "full_pipeline", latency_ms=380, llm_calls=3, intent="general_query", took_shortcut=False),
    ]
    summary = summarize(results)

    assert summary["adaptive"]["n"] == 2
    assert summary["full_pipeline"]["n"] == 2
    assert summary["adaptive"]["shortcut_taken_count"] == 2
    assert summary["full_pipeline"]["shortcut_taken_count"] == 0

    # Adaptive should show a real, positive latency and call-count
    # reduction versus always running the full pipeline.
    assert summary["comparison"]["latency_reduction_pct"] > 0
    assert summary["comparison"]["llm_call_reduction_pct"] > 0
    assert summary["comparison"]["intent_disagreement_count"] == 0


def test_summarize_flags_intent_disagreement_between_configs():
    # If the shortcut changes the final predicted intent versus the full
    # pipeline for the SAME message, that's a real correctness concern
    # the benchmark must surface, not silently average away.
    results = [
        _run("q1", "adaptive", latency_ms=100, llm_calls=1, intent="general_query", took_shortcut=True),
        _run("q1", "full_pipeline", latency_ms=400, llm_calls=3, intent="billing_issue", took_shortcut=False),
    ]
    summary = summarize(results)
    assert summary["comparison"]["intent_disagreement_count"] == 1
    assert "q1" in summary["comparison"]["intent_disagreement_messages"]
