from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    ticket_required: bool
    ticket_id: str
    response: str
    escalation_required: bool