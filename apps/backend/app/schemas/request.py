from typing import Optional

from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=5000,
        description="Customer support message",
    )

    customer_id: Optional[str] = None

    conversation_id: Optional[str] = None

    language: str = "en"

    channel: str = "web"