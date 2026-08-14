import logging

from ai_core.observability.decorators import traced
from ai_core.agents.base_agent import BaseAgent
from ai_core.models.response import ResponseOutput
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer, record_llm_fallback, increment_llm_calls
from ai_core.llm.service import llm_service
from ai_core.prompts.response_prompt import response_prompt
from ai_core.error_handling import with_fallback, RESPONSE_FALLBACK
import ai_core.tools

logger = logging.getLogger(__name__)


class ResponseAgent(BaseAgent):

    @with_fallback("response_agent", RESPONSE_FALLBACK)
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

        knowledge = state.tool_results.get("knowledge")
        ticket = state.tool_results.get("ticket")
        memory = state.tool_results.get("memory")

        # Build context for LLM synthesis
        context_parts = []
        if knowledge:
            context_parts.append(str(knowledge))
        
        if memory:
            context_parts.append(f"Previous conversation: {memory}")

        context = "\n\n".join(context_parts) if context_parts else "No additional context available."

        # Generate synthesized response using LLM
        try:
            logger.debug("=" * 80)
            logger.debug("ResponseAgent - Calling LLM with:")
            logger.debug(f"  user_message: {state.request.message}")
            logger.debug(f"  intent: {intent_label}")
            logger.debug(f"  knowledge_context: {context[:100]}...")
            logger.debug(f"  ticket_id: {ticket.ticket_id if ticket else None}")
            logger.debug("=" * 80)
            
            synthesized_response = await llm_service.generate_structured(
                prompt=response_prompt,
                output_schema=ResponseOutput,
                variables={
                    "user_message": state.request.message,
                    "intent": intent_label,
                    "knowledge_context": context,
                    "ticket_id": ticket.ticket_id if ticket else None,
                },
            )
            
            increment_llm_calls(state)
            
            logger.debug("=" * 80)
            logger.debug("ResponseAgent - LLM returned:")
            logger.debug(f"  synthesized_response: {synthesized_response}")
            logger.debug(f"  synthesized_response.response: {synthesized_response.response}")
            logger.debug("=" * 80)
            
            response_text = synthesized_response.response
        except Exception as e:
            # Fallback to simple concatenation if LLM fails
            record_llm_fallback(state, "response_agent")
            parts = []
            if knowledge:
                parts.append(str(knowledge))
            if ticket:
                parts.append(f"Ticket created: {ticket.ticket_id}")
            if memory:
                parts.append(f"Conversation context: {memory}")
            if not parts:
                parts.append("I can help with your request.")
            parts.append(f"We detected that your request is related to '{intent_label}'.")
            response_text = "\n\n".join(parts)

        follow_up_actions = []
        if ticket is not None and getattr(ticket, "ticket_required", False):
            follow_up_actions.append("Check your support ticket status.")

        state.response = ResponseOutput(
            response=response_text,
            tone="professional",
            follow_up_actions=follow_up_actions,
            confidence=confidence,
        )

        logger.debug("=" * 80)
        logger.debug("ResponseAgent - Generated response_text:")
        logger.debug(response_text)
        logger.debug("")
        logger.debug("ResponseAgent - State.response:")
        logger.debug(state.response)
        logger.debug("=" * 80)

        # Conversation history saving is handled by SupportService.process_request()
        # to ensure single source of truth for memory management

        record_agent_execution(state, "response", started_at, details="response generated")
        return state