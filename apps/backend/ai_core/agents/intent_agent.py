from ai_core.agents.base_agent import BaseAgent
from ai_core.llm.service import llm_service
from ai_core.prompts.intent_prompt import intent_prompt
from ai_core.models.intent import IntentOutput
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import increment_llm_calls, record_agent_execution, start_agent_timer
from ai_core.error_handling import with_fallback, INTENT_FALLBACK


class IntentAgent(BaseAgent):

    @with_fallback("intent_agent", INTENT_FALLBACK)
    async def execute(
        self,
        state: SupportState,
    ) -> SupportState:
        started_at = start_agent_timer()

        result = await llm_service.generate_structured(
            prompt=intent_prompt,
            output_schema=IntentOutput,
            variables={
                "message": state.request.message
            },
        )

        increment_llm_calls(state)
        state.intent = result
        record_agent_execution(state, "intent", started_at, details="intent detection completed")

        return state