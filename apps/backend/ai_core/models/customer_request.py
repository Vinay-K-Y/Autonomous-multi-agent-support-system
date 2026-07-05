from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class CustomerRequest(BaseModel):

    message: str = Field(
        description="Customer's support message"
    )

    customer_id: Optional[str] = None

    conversation_id: str = Field(default_factory=lambda: str(uuid4()))

    language: str = "en"

    attachments: List[str] = Field(default_factory=list)

    channel: str = "web"

    metadata: dict = Field(default_factory=dict)