from uuid import uuid4

from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState


class SupportStateFactory:
    """
    Builds a fully initialized SupportState.

    Centralizing state creation ensures every workflow starts
    with the same defaults.
    """

    @staticmethod
    def create(
        message: str,
        customer_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
        channel: str = "web",
        conversation_history: str | None = None,
    ) -> SupportState:

        if conversation_id is None:
            conversation_id = str(uuid4())

        request = CustomerRequest(
            message=message,
            customer_id=customer_id,
            conversation_id=conversation_id,
            language=language,
            channel=channel,
        )

        metadata = ProcessingMetadata(
            request_id=str(uuid4())
        )

        return SupportState(
            request=request,
            metadata=metadata,
            conversation_history=conversation_history or "",
        )