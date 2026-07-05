from ai_core.agents.base_agent import BaseAgent
from ai_core.memory.conversation_manager import conversation_manager
from ai_core.models.response import ResponseOutput
from ai_core.state.support_state import SupportState
from ai_core.tools.executor import tool_executor
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer
import ai_core.tools


class ResponseAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()
        intent_label = state.intent.intent.value if state.intent is not None else "general_query"
        knowledge_answer = state.knowledge.answer if state.knowledge is not None else "I can help with your request."
        confidence = 0.0

        if state.knowledge is not None:
            confidence = state.knowledge.confidence
        elif state.intent is not None:
            confidence = state.intent.confidence

        conversation = getattr(state, "conversation_history", "")
        answer = tool_executor.execute(
            "knowledge",
            question=state.request.message,
            conversation=conversation,
        )

        response_parts = [knowledge_answer]
        response_parts.append(
            f"We detected that your request is related to '{intent_label}'."
        )
        response_parts.append(answer)

        follow_up_actions = []

        if state.ticket is not None and state.ticket.ticket_required:
            response_parts.append(
                f"A support ticket has been created for you ({state.ticket.ticket_id})."
            )
            follow_up_actions.append("Check your support ticket status.")

        if state.human_review.required:
            follow_up_actions.append("A specialist will review your case.")

        state.response = ResponseOutput(
            response="\n\n".join(response_parts),
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