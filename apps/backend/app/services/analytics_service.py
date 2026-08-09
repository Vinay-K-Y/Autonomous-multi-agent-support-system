from typing import Dict, Any
from ai_core.state.support_state import SupportState


class AnalyticsService:
    """Service for aggregating and exposing workflow metrics."""

    def __init__(self):
        # In-memory storage for recent request metrics
        self._recent_requests: list[SupportState] = []

    def record_request(self, state: SupportState) -> None:
        """Record a completed request for metrics aggregation."""
        self._recent_requests.append(state)
        # Keep only last 100 requests to avoid memory bloat
        if len(self._recent_requests) > 100:
            self._recent_requests.pop(0)

    def metrics(self) -> Dict[str, Any]:
        """Return aggregate metrics from recent requests."""
        if not self._recent_requests:
            return {
                "total_requests": 0,
                "llm_fallback_count": 0,
                "llm_fallback_rate": 0.0,
                "avg_llm_calls": 0.0,
                "avg_processing_time_ms": 0.0,
            }

        total_requests = len(self._recent_requests)
        total_fallbacks = sum(
            state.metadata.llm_fallback_count for state in self._recent_requests
        )
        total_llm_calls = sum(
            state.metadata.llm_call_count for state in self._recent_requests
        )
        total_processing_time = sum(
            state.metadata.processing_time_ms for state in self._recent_requests
        )

        return {
            "total_requests": total_requests,
            "llm_fallback_count": total_fallbacks,
            "llm_fallback_rate": total_fallbacks / total_requests if total_requests > 0 else 0.0,
            "avg_llm_calls": total_llm_calls / total_requests if total_requests > 0 else 0.0,
            "avg_processing_time_ms": total_processing_time / total_requests if total_requests > 0 else 0.0,
        }

    def get_request_trace(self, request_id: str) -> Dict[str, Any] | None:
        """Get detailed trace for a specific request by request_id."""
        for state in self._recent_requests:
            if state.metadata.request_id == request_id:
                return {
                    "request_id": state.metadata.request_id,
                    "processing_time_ms": state.metadata.processing_time_ms,
                    "llm_call_count": state.metadata.llm_call_count,
                    "llm_fallback_count": state.metadata.llm_fallback_count,
                    "retrieved_documents": state.metadata.retrieved_documents,
                    "agent_timings": state.metadata.agent_timings,
                    "routing_reasons": state.metadata.routing_reasons,
                }
        return None


analytics_service = AnalyticsService()
