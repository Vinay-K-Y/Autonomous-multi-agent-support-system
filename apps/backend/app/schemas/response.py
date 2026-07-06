from typing import Optional

from pydantic import BaseModel


class TicketResponse(BaseModel):

    ticket_required: bool

    ticket_id: Optional[str] = None

    priority: Optional[str] = None

    assigned_team: Optional[str] = None


class SupportResponse(BaseModel):

    workflow_id: str

    conversation_id: str

    response: str

    confidence: float

    intent: Optional[str] = None

    ticket: Optional[TicketResponse] = None

    planner_used: bool

    knowledge_used: bool

    human_review_required: bool