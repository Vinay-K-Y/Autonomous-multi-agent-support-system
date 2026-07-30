import uuid

from ai_core.models.ticket import TicketOutput
from ai_core.tools.base_tool import BaseTool


class TicketTool(BaseTool):

    name = "ticket"
    description = "Creates a customer support ticket."

    def execute(
        self,
        priority: str = "medium",
        summary: str | None = None,
        description: str | None = None,
        **kwargs,
    ):

        return TicketOutput(
            ticket_required=True,
            ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            priority=priority,
            assigned_team="Customer Support",
            summary=summary,
            description=description,
        )