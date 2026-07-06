from typing import Optional

from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    """
    Incoming support request received by the API.
    """

    message: str = Field(
        ...,
        description="Customer support message",
        examples=["How do I get a refund?"],
    )

    customer_id: Optional[str] = None

    conversation_id: Optional[str] = None

    language: str = "en"

    channel: str = "web"

    metadata: dict = Field(default_factory=dict)