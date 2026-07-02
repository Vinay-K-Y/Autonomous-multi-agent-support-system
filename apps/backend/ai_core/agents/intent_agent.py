from ai_core.agents.base_agent import BaseAgent
from ai_core.state.support_state import SupportState


class IntentAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

        query = state["user_query"].lower()

        if "refund" in query:
            state["intent"] = "refund"

        elif "payment" in query:
            state["intent"] = "billing"

        elif "broken" in query or "damaged" in query:
            state["intent"] = "technical"

        else:
            state["intent"] = "general"

        state["confidence"] = 0.85

        return state