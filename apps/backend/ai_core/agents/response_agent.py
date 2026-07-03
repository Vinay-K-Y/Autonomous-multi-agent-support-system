from ai_core.agents.base_agent import BaseAgent
from ai_core.models.response import ResponseOutput
from ai_core.state.support_state import SupportState


class ResponseAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

        response = (
            f"{state.knowledge.answer}\n\n"
            f"We detected that your request is related to "
            f"'{state.intent.intent.value}'."
        )

        if (
            state.ticket is not None
            and state.ticket.ticket_required
        ):
            response += (
                f"\n\nA support ticket has been created for you "
                f"({state.ticket.ticket_id})."
            )

        state.response = ResponseOutput(
            response=response,
            tone="professional",
            confidence=0.98,
        )

        return state