import uuid


class JiraClient:
    """
    Mock Jira integration.

    Later this will communicate with the real Jira REST API.
    """

    def create_ticket(
        self,
        summary: str,
        description: str,
        priority: str = "Medium",
    ) -> dict:

        return {
            "ticket_id": f"TKT-{uuid.uuid4().hex[:8].upper()}",
            "summary": summary,
            "priority": priority,
            "status": "OPEN",
        }