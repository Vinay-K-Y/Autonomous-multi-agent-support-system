from ai_core.tools.ticket_tool import TicketTool


def test_ticket_tool():

    tool = TicketTool()

    ticket = tool.execute(
        summary="Refund request",
        description="Customer requested a refund.",
        priority="High",
    )

    assert ticket["ticket_id"].startswith("TKT-")
    assert ticket["status"] == "OPEN"