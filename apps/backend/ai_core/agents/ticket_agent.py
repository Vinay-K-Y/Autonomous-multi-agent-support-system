from ai_core.agents.base_agent import BaseAgent
from ai_core.models.ticket import TicketOutput
from ai_core.state.support_state import SupportState
from ai_core.tools.executor import tool_executor
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer
import ai_core.tools


class TicketAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()
        intent_value = state.intent.intent.value if state.intent is not None else None
        ticket_required = intent_value in {"refund", "technical_issue", "technical"}

        if ticket_required:
            state.ticket = tool_executor.execute(
                "ticket",
                priority="high",
            )
        else:
            state.ticket = TicketOutput(
                ticket_required=False,
                priority="low",
            )

        record_agent_execution(state, "ticket", started_at, details="ticket decision completed")
        return state