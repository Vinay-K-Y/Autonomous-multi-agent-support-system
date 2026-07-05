from dataclasses import dataclass

from ai_core.models.intent import IntentType


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

    escalation_threshold: float = 0.7
    knowledge_confidence_threshold: float = 0.8
    default_tone: str = "professional"


WORKFLOW_RULES = WorkflowRules()
