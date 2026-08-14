from __future__ import annotations

from ai_core.calibration.provider import CalibratedThresholdProvider, calibrated_threshold_provider
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
    def __init__(self, rules=None, threshold_provider: CalibratedThresholdProvider | None = None):
        self.rules = rules or WORKFLOW_RULES
        # Falls back to settings.ESCALATION_THRESHOLD (self.rules.escalation_threshold)
        # whenever no valid calibration artifact exists — see
        # ai_core/calibration/provider.py for details of the guarantee.
        self.threshold_provider = threshold_provider or calibrated_threshold_provider

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
        threshold, threshold_source = self.threshold_provider.get_escalation_threshold()

        if confidence < threshold:
            return True, (
                f"Confidence {confidence:.2f} is below the escalation threshold "
                f"{threshold:.2f} [{threshold_source}]."
            )

        return False, (
            f"Confidence {confidence:.2f} is above the escalation threshold "
            f"{threshold:.2f} [{threshold_source}]."
        )

    def evaluate(self, state: SupportState) -> DecisionResult:
        modified_plan = state.execution_plan
        blocked_tools = []
        
        # Check if escalation is needed as a deterministic backstop
        should_escalate, escalation_reason = self.should_escalate(state)
        
        if should_escalate:
            # Check if plan already includes human_review
            has_human_review = any(
                tc.tool == "human_review" 
                for tc in modified_plan.tool_calls
            )
            
            if not has_human_review:
                from ai_core.models.tool_call import ToolCall
                
                # Add human_review tool call to the plan
                escalation_tool = ToolCall(
                    tool="human_review",
                    parameters={"reason": escalation_reason}
                )
                
                # Create modified plan with human_review added
                modified_plan = modified_plan.model_copy(
                    update={
                        "tool_calls": modified_plan.tool_calls + [escalation_tool],
                        "reasoning": f"{modified_plan.reasoning or ''} Added human_review: {escalation_reason}"
                    }
                )
        
        # Check if ticket creation is needed
        should_create_ticket, ticket_reason = self.should_create_ticket(state)
        if should_create_ticket:
            has_ticket = any(
                tc.tool == "ticket" 
                for tc in modified_plan.tool_calls
            )
            
            if not has_ticket:
                from ai_core.models.tool_call import ToolCall
                
                # Add ticket tool call to the plan
                ticket_tool = ToolCall(
                    tool="ticket",
                    parameters={"priority": "medium"}
                )
                
                modified_plan = modified_plan.model_copy(
                    update={
                        "tool_calls": modified_plan.tool_calls + [ticket_tool],
                        "reasoning": f"{modified_plan.reasoning or ''} Added ticket: {ticket_reason}"
                    }
                )
        
        # Check if knowledge retrieval is needed
        should_retrieve_knowledge, knowledge_reason = self.should_retrieve_knowledge(state)
        if should_retrieve_knowledge:
            has_knowledge = any(
                tc.tool == "knowledge" 
                for tc in modified_plan.tool_calls
            )
            
            if not has_knowledge:
                from ai_core.models.tool_call import ToolCall
                
                # Add knowledge tool call to the plan
                knowledge_tool = ToolCall(
                    tool="knowledge",
                    parameters={"question": state.request.message}
                )
                
                modified_plan = modified_plan.model_copy(
                    update={
                        "tool_calls": modified_plan.tool_calls + [knowledge_tool],
                        "reasoning": f"{modified_plan.reasoning or ''} Added knowledge: {knowledge_reason}"
                    }
                )
        
        # Remove tools that don't apply (conservative approach)
        # Example: if high confidence general_query, don't need ticket
        if state.intent and state.intent.confidence > 0.85:
            if state.intent.intent.value == "general_query":
                # Remove ticket if present for high-confidence general queries
                modified_tool_calls = [
                    tc for tc in modified_plan.tool_calls 
                    if tc.tool != "ticket"
                ]
                if len(modified_tool_calls) < len(modified_plan.tool_calls):
                    blocked_tools.append("ticket")
                    modified_plan = modified_plan.model_copy(
                        update={
                            "tool_calls": modified_tool_calls,
                            "reasoning": f"{modified_plan.reasoning or ''} Removed ticket: high confidence general query"
                        }
                    )
        
        return DecisionResult(
            approved=True,
            reasoning="Execution plan approved.",
            modified_plan=modified_plan,
            blocked_tools=blocked_tools,
            escalation_threshold_used=self.threshold_provider.get_escalation_threshold()[0],
        )

    def record_agent(self, state: SupportState, agent_name: str, *, details: str | None = None, extra: dict | None = None) -> None:
        started_at = start_agent_timer()
        record_agent_execution(state, agent_name, started_at, details=details, extra=extra)

    def track_knowledge(self, state: SupportState, document_count: int) -> None:
        mark_documents_retrieved(state, document_count)

    def track_llm_call(self, state: SupportState, count: int = 1) -> None:
        increment_llm_calls(state, count)