from ai_core.agents.base_agent import BaseAgent
from ai_core.llm.service import llm_service
from ai_core.prompts.intent_prompt import intent_prompt
from ai_core.models.intent import IntentOutput
from ai_core.state.support_state import SupportState


class IntentAgent(BaseAgent):

    async def execute(
        self,
        state: SupportState,
    ) -> SupportState:

        result = await llm_service.generate_structured(
            prompt=intent_prompt,
            output_schema=IntentOutput,
            variables={
                "message": state.request.message
            },
        )

        state.intent = result

        return state