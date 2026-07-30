from typing import Optional

from pydantic import BaseModel


class TicketOutput(BaseModel):
    ticket_required: bool = False

    ticket_id: Optional[str] = None

    priority: str = "low"

    assigned_team: Optional[str] = None

    summary: Optional[str] = None

    description: Optional[str] = None