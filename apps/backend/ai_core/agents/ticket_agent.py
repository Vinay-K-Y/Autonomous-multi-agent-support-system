from uuid import uuid4

from ai_core.agents.base_agent import BaseAgent
from ai_core.models.ticket import TicketOutput
from ai_core.state.support_state import SupportState


class TicketAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

        ticket_required = (
            state.intent is not None
            and state.intent.intent.value in ["refund", "technical"]
        )

        if ticket_required:

            state.ticket = TicketOutput(
                ticket_required=True,
                ticket_id=f"TKT-{str(uuid4())[:8].upper()}",
                priority="high",
                assigned_team="Customer Support",
            )

        else:

            state.ticket = TicketOutput(
                ticket_required=False,
                priority="low",
            )

        return state