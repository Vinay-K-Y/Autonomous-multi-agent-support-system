from __future__ import annotations

from ai_core.models.decision import DecisionResult
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import (
    increment_llm_calls,
    mark_documents_retrieved,
    record_agent_execution,
    start_agent_timer,
)
from ai_core.workflow.rules import WORKFLOW_RULES


class DecisionEngine:
    def __init__(self, rules=None):
        self.rules = rules or WORKFLOW_RULES

    def route_after_intent(self, state: SupportState) -> str:
        if state.intent is None:
            reason = "No intent detected yet; defaulting to knowledge retrieval."
            state.metadata.routing_reasons.append(reason)
            return "knowledge"

        intent_value = state.intent.intent.value
        if intent_value in {"refund", "technical_issue", "technical"}:
            reason = f"Intent '{intent_value}' requires a ticketing path."
            state.metadata.routing_reasons.append(reason)
            return "ticket"

        reason = f"Intent '{intent_value}' follows the knowledge-only path."
        state.metadata.routing_reasons.append(reason)
        return "knowledge"

    def should_retrieve_knowledge(self, state: SupportState) -> tuple[bool, str]:
        if state.intent is None:
            return True, "No intent yet, so knowledge retrieval is the safe default."

        intent = state.intent.intent
        if intent in self.rules.knowledge_intents:
            return True, f"Intent '{intent.value}' should use knowledge retrieval."

        return False, f"Intent '{intent.value}' does not require knowledge retrieval."

    def should_create_ticket(self, state: SupportState) -> tuple[bool, str]:
        if state.intent is None:
            return False, "No intent available; ticket creation skipped."

        intent = state.intent.intent
        if intent in self.rules.ticket_intents:
            return True, f"Intent '{intent.value}' triggers ticket creation."

        return False, f"Intent '{intent.value}' does not require a ticket."

    def should_escalate(self, state: SupportState) -> tuple[bool, str]:
        if state.intent is None:
            return False, "No intent available; no escalation required."

        confidence = state.intent.confidence
        if confidence < self.rules.escalation_threshold:
            return True, f"Confidence {confidence:.2f} is below the escalation threshold {self.rules.escalation_threshold:.2f}."

        return False, f"Confidence {confidence:.2f} is above the escalation threshold {self.rules.escalation_threshold:.2f}."

    def evaluate(self, state: SupportState) -> DecisionResult:
        return DecisionResult(
            approved=True,
            reasoning="Execution plan approved.",
            modified_plan=state.execution_plan,
        )

    def record_agent(self, state: SupportState, agent_name: str, *, details: str | None = None, extra: dict | None = None) -> None:
        started_at = start_agent_timer()
        record_agent_execution(state, agent_name, started_at, details=details, extra=extra)

    def track_knowledge(self, state: SupportState, document_count: int) -> None:
        mark_documents_retrieved(state, document_count)

    def track_llm_call(self, state: SupportState, count: int = 1) -> None:
        increment_llm_calls(state, count)