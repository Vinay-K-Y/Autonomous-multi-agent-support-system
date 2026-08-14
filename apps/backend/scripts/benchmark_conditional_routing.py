"""Empirically measure what the conditional routing shortcut (Task 1 —
route_after_intent skipping planner/decision/tool_executor for
high-confidence general queries) actually buys, compared to always
running the full pipeline.

For each query in the benchmark set, this runs the real graph TWICE:
  1. Adaptive (state.force_full_pipeline=False) — whatever the graph
     would normally decide.
  2. Full pipeline (state.force_full_pipeline=True) — forces the
     planner/decision/tool_executor path regardless of intent/confidence.

It measures, per configuration:
  - wall-clock latency (p50, p95)
  - LLM call count (state.metadata.llm_call_count)
  - which path was actually taken (routing_reasons)
  - whether the two configurations produced the same final intent
    (a proxy for "did the shortcut change the answer")

This requires a working LLM provider configured via .env (real network
calls, same as the rest of the app) — there is no offline/mocked mode,
because the entire point is to measure real latency and real call counts.

Usage:
    python scripts/benchmark_conditional_routing.py \
        --queries ai_core/benchmarks/data/routing_benchmark_queries.jsonl \
        --output ai_core/benchmarks/data/routing_benchmark_results.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class RunResult:
    message: str
    query_type: str
    config: str  # "adaptive" or "full_pipeline"
    latency_ms: float
    llm_call_count: int
    predicted_intent: str | None
    confidence: float | None
    took_shortcut: bool
    routing_reasons: list[str] = field(default_factory=list)


async def run_one(message: str, query_type: str, force_full_pipeline: bool) -> RunResult:
    # Imported lazily so the pure aggregation/statistics functions in this
    # module (RunResult, _percentile, summarize) can be unit tested
    # without pulling in the full LangGraph/LangChain dependency chain —
    # see tests/test_benchmark_conditional_routing.py.
    from ai_core.factories.support_state_factory import SupportStateFactory
    from ai_core.graph.builder import support_graph

    state = SupportStateFactory.create(message=message)
    state.force_full_pipeline = force_full_pipeline

    start = time.perf_counter()
    result_state = await support_graph.ainvoke(state)
    elapsed_ms = (time.perf_counter() - start) * 1000

    took_shortcut = (
        result_state.execution_plan is None and not force_full_pipeline
    )

    return RunResult(
        message=message,
        query_type=query_type,
        config="full_pipeline" if force_full_pipeline else "adaptive",
        latency_ms=elapsed_ms,
        llm_call_count=result_state.metadata.llm_call_count,
        predicted_intent=(
            result_state.intent.intent.value if result_state.intent else None
        ),
        confidence=(
            result_state.intent.confidence if result_state.intent else None
        ),
        took_shortcut=took_shortcut,
        routing_reasons=list(result_state.metadata.routing_reasons),
    )


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (p / 100)
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def summarize(results: list[RunResult]) -> dict:
    summary = {}
    for config in ("adaptive", "full_pipeline"):
        subset = [r for r in results if r.config == config]
        latencies = [r.latency_ms for r in subset]
        call_counts = [r.llm_call_count for r in subset]
        summary[config] = {
            "n": len(subset),
            "latency_ms_p50": round(_percentile(latencies, 50), 1),
            "latency_ms_p95": round(_percentile(latencies, 95), 1),
            "mean_llm_call_count": round(statistics.mean(call_counts), 2) if call_counts else 0,
            "shortcut_taken_count": sum(1 for r in subset if r.took_shortcut),
        }

    adaptive_mean_latency = statistics.mean([r.latency_ms for r in results if r.config == "adaptive"]) if results else 0
    full_mean_latency = statistics.mean([r.latency_ms for r in results if r.config == "full_pipeline"]) if results else 0
    adaptive_mean_calls = statistics.mean([r.llm_call_count for r in results if r.config == "adaptive"]) if results else 0
    full_mean_calls = statistics.mean([r.llm_call_count for r in results if r.config == "full_pipeline"]) if results else 0

    # Accuracy proxy: did forcing the full pipeline change the predicted
    # intent versus the adaptive shortcut, for the same message? If the
    # shortcut is safe, these should agree essentially always.
    by_message: dict[str, dict[str, RunResult]] = {}
    for r in results:
        by_message.setdefault(r.message, {})[r.config] = r
    disagreements = [
        msg for msg, cfgs in by_message.items()
        if "adaptive" in cfgs and "full_pipeline" in cfgs
        and cfgs["adaptive"].predicted_intent != cfgs["full_pipeline"].predicted_intent
    ]

    summary["comparison"] = {
        "latency_reduction_pct": (
            round(100 * (1 - adaptive_mean_latency / full_mean_latency), 1)
            if full_mean_latency else 0
        ),
        "llm_call_reduction_pct": (
            round(100 * (1 - adaptive_mean_calls / full_mean_calls), 1)
            if full_mean_calls else 0
        ),
        "intent_disagreement_count": len(disagreements),
        "intent_disagreement_messages": disagreements,
    }
    return summary


async def main_async(queries_path: Path, output_path: Path) -> None:
    with queries_path.open() as f:
        queries = [json.loads(line) for line in f if line.strip()]

    results: list[RunResult] = []
    for i, q in enumerate(queries, start=1):
        message = q["message"]
        query_type = q["query_type"]

        adaptive = await run_one(message, query_type, force_full_pipeline=False)
        full = await run_one(message, query_type, force_full_pipeline=True)
        results.extend([adaptive, full])

        print(
            f"[{i}/{len(queries)}] {query_type!r:28} "
            f"adaptive={adaptive.latency_ms:7.1f}ms/{adaptive.llm_call_count}calls "
            f"full={full.latency_ms:7.1f}ms/{full.llm_call_count}calls "
            f"shortcut_taken={adaptive.took_shortcut}"
        )

    summary = summarize(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "summary": summary,
                "raw_results": [asdict(r) for r in results],
            },
            indent=2,
        )
    )

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
    print(f"\nFull results written to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queries",
        type=Path,
        default=Path("ai_core/benchmarks/data/routing_benchmark_queries.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ai_core/benchmarks/data/routing_benchmark_results.json"),
    )
    args = parser.parse_args()
    asyncio.run(main_async(args.queries, args.output))


if __name__ == "__main__":
    main()
