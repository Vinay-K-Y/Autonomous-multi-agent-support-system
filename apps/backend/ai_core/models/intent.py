from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    REFUND = "refund"
    TECHNICAL_ISSUE = "technical_issue"
    BILLING = "billing_issue"
    DELIVERY = "delivery_issue"
    ACCOUNT = "account_issue"
    GENERAL = "general_query"
    OTHER = "other"


class IntentOutput(BaseModel):
    intent: IntentType = Field(
        description="Detected customer intent"
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score"
    )

    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen"
    )