from __future__ import annotations

from time import perf_counter
from typing import Any

from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState


def start_agent_timer() -> float:
    return perf_counter()


def record_agent_execution(
    state: SupportState,
    agent_name: str,
    started_at: float,
    *,
    details: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    elapsed_ms = round((perf_counter() - started_at) * 1000, 2)
    state.metadata.agent_timings[agent_name] = elapsed_ms

    if details:
        state.metadata.routing_reasons.append(f"{agent_name}: {details}")

    if extra:
        for key, value in extra.items():
            setattr(state.metadata, key, value)


def increment_llm_calls(state: SupportState, count: int = 1) -> None:
    state.metadata.llm_call_count += count


def mark_documents_retrieved(state: SupportState, count: int) -> None:
    state.metadata.retrieved_documents = count


def record_llm_fallback(state: SupportState, component: str) -> None:
    """Record when an LLM call falls back to non-LLM logic."""
    state.metadata.llm_fallback_count += 1
    state.metadata.routing_reasons.append(f"LLM fallback in {component}")


def finalize_processing_time(state: SupportState, started_at: float | None = None) -> None:
    if started_at is None:
        started_at = state.metadata.started_at.timestamp()

    state.metadata.processing_time_ms = round((perf_counter() - started_at) * 1000, 2)
