from ai_core.agents.base_agent import BaseAgent
from ai_core.models.response import ResponseOutput
from ai_core.state.support_state import SupportState


class ResponseAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

        state.response = ResponseOutput(
            response=f"Intent detected: {state.intent.intent.value}",
            tone="professional",
            confidence=1.0,
        )

        return state