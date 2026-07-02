from typing import TypedDict


class SupportState(TypedDict):
    user_query: str
    intent: str
    confidence: float
    retrieved_documents: list[str]
    ticket_required: bool
    ticket_id: str
    escalation_required: bool
    final_response: str