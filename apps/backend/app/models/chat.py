from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str


class ChatResponse(BaseModel):

    intent: str

    confidence: float

    ticket_required: bool

    ticket_id: Optional[str] = None

    response: str

    escalation_required: bool