from ai_core.agents.base_agent import BaseAgent
from ai_core.memory.conversation_manager import conversation_manager
from ai_core.models.response import ResponseOutput
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer
import ai_core.tools


class ResponseAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()
        decision = state.decision

        if decision is not None and not decision.approved:
            state.response = ResponseOutput(
                response=decision.reasoning,
                confidence=1.0,
                tone="professional",
            )
            record_agent_execution(state, "response", started_at, details="decision blocked response")
            return state

        intent_label = state.intent.intent.value if state.intent is not None else "general_query"
        confidence = 0.0

        if state.intent is not None:
            confidence = state.intent.confidence

        parts = []
        knowledge = state.tool_results.get("knowledge")
        ticket = state.tool_results.get("ticket")
        memory = state.tool_results.get("memory")

        if knowledge:
            parts.append(str(knowledge))

        if ticket:
            parts.append(f"Ticket created: {ticket.ticket_id}")

        if memory:
            parts.append(f"Conversation context: {memory}")

        if not parts:
            parts.append("I can help with your request.")

        parts.append(
            f"We detected that your request is related to '{intent_label}'."
        )

        follow_up_actions = []
        if ticket is not None and getattr(ticket, "ticket_required", False):
            follow_up_actions.append("Check your support ticket status.")

        state.response = ResponseOutput(
            response="\n\n".join(parts),
            tone="professional",
            follow_up_actions=follow_up_actions,
            confidence=confidence,
        )

        conversation_manager.add_user_message(
            state.request.conversation_id,
            state.request.message,
        )
        conversation_manager.add_assistant_message(
            state.request.conversation_id,
            state.response.response,
        )

        record_agent_execution(state, "response", started_at, details="response generated")
        return state