from dataclasses import dataclass

from ai_core.models.intent import IntentType
from app.core.config import settings


@dataclass(frozen=True)
class WorkflowRules:
    knowledge_intents: tuple[IntentType, ...] = (
        IntentType.REFUND,
        IntentType.TECHNICAL_ISSUE,
        IntentType.BILLING,
        IntentType.DELIVERY,
        IntentType.ACCOUNT,
        IntentType.GENERAL,
        IntentType.OTHER,
    )

    ticket_intents: tuple[IntentType, ...] = (
        IntentType.REFUND,
        IntentType.TECHNICAL_ISSUE,
    )

    escalation_threshold: float = settings.ESCALATION_THRESHOLD
    knowledge_confidence_threshold: float = settings.KNOWLEDGE_CONFIDENCE_THRESHOLD
    default_tone: str = "professional"


WORKFLOW_RULES = WorkflowRules()
