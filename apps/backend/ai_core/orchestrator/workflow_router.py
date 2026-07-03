from ai_core.models.intent import IntentType
from ai_core.state.support_state import SupportState


class WorkflowRouter:
    """
    Decides which workflow should be executed
    based on the current SupportState.
    """

    def get_workflow(self, state: SupportState) -> list[str]:

        # Default workflow
        workflow = [
            "intent",
            "knowledge",
            "response",
        ]

        # If intent is not known yet, start with IntentAgent
        if state.intent is None:
            return workflow

        # Refunds require ticket + review
        if state.intent.intent == IntentType.REFUND:
            return [
                "knowledge",
                "ticket",
                "human_review",
                "response",
            ]

        # Returns require ticket
        if state.intent.intent == IntentType.RETURN:
            return [
                "knowledge",
                "ticket",
                "response",
            ]

        # Technical issues require ticket
        if state.intent.intent == IntentType.TECHNICAL_SUPPORT:
            return [
                "knowledge",
                "ticket",
                "response",
            ]

        # FAQs don't need tickets
        return [
            "knowledge",
            "response",
        ]