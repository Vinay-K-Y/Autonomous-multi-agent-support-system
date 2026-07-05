from datetime import datetime, UTC
from typing import Literal

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """
    Represents one message inside a conversation.
    """

    role: Literal[
        "system",
        "user",
        "assistant",
    ]

    content: str

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class ConversationHistory(BaseModel):
    """
    Complete conversation history.
    """

    conversation_id: str

    messages: list[ConversationMessage] = Field(
        default_factory=list
    )