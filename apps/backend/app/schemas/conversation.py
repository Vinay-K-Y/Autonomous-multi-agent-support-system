from datetime import datetime

from pydantic import BaseModel


class ConversationSummary(BaseModel):

    conversation_id: str

    created_at: datetime

    last_updated: datetime

    message_count: int