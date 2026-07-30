from ai_core.models.ticket import TicketOutput
from ai_core.tools.ticket_tool import TicketTool


def test_ticket_tool():

    tool = TicketTool()

    ticket = tool.execute(
        summary="Refund request",
        description="Customer requested a refund.",
        priority="High",
    )

    assert isinstance(ticket, TicketOutput)
    assert ticket.ticket_required is True
    assert ticket.ticket_id.startswith("TKT-")
    assert ticket.priority == "High"
    assert ticket.summary == "Refund request"
    assert ticket.description == "Customer requested a refund."