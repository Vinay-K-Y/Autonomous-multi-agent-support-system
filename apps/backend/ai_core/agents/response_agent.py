from ai_core.agents.base_agent import BaseAgent
from ai_core.state.support_state import SupportState


class ResponseAgent(BaseAgent):

    async def execute(self, state: SupportState):

        state["final_response"] = (
            f"Intent detected: {state['intent']}."
        )

        return state