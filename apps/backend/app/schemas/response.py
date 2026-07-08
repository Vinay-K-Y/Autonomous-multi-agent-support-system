from typing import Optional

from pydantic import BaseModel


class SupportResponse(BaseModel):

    conversation_id: str

    response: str

    intent: Optional[str]

    confidence: float

    ticket_id: Optional[str]

    requires_human_review: bool

    processing_time_ms: float