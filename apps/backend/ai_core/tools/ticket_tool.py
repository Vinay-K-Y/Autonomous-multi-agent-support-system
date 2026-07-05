import uuid

from ai_core.models.ticket import TicketOutput
from ai_core.tools.base_tool import BaseTool


class TicketTool(BaseTool):

    name = "ticket"

    def execute(
        self,
        priority: str = "medium",
    ):

        return TicketOutput(
            ticket_required=True,
            ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            priority=priority,
            assigned_team="Customer Support",
        )