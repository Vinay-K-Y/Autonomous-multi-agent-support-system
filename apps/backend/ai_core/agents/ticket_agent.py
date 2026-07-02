from ai_core.agents.base_agent import BaseAgent
from ai_core.state.support_state import SupportState


class TicketAgent(BaseAgent):

    async def execute(self, state: SupportState):

        if state["intent"] in ["refund", "technical"]:

            state["ticket_required"] = True
            state["ticket_id"] = "TKT-1001"

        return state