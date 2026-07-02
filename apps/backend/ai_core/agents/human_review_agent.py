from ai_core.agents.base_agent import BaseAgent
from ai_core.state.support_state import SupportState


class HumanReviewAgent(BaseAgent):

    async def execute(self, state: SupportState):

        if state["confidence"] < 0.70:

            state["escalation_required"] = True

        return state