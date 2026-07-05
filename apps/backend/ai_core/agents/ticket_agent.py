from uuid import uuid4

from ai_core.agents.base_agent import BaseAgent
from ai_core.models.ticket import TicketOutput
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer


class TicketAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()
        intent_value = state.intent.intent.value if state.intent is not None else None
        ticket_required = intent_value in {"refund", "technical_issue", "technical"}

        if ticket_required:
            assigned_team = "Technical Support" if intent_value == "technical_issue" else "Customer Support"
            state.ticket = TicketOutput(
                ticket_required=True,
                ticket_id=f"TKT-{str(uuid4())[:8].upper()}",
                priority="high",
                assigned_team=assigned_team,
            )
        else:
            state.ticket = TicketOutput(
                ticket_required=False,
                priority="low",
            )

        record_agent_execution(state, "ticket", started_at, details="ticket decision completed")
        return state