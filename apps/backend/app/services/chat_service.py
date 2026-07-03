from uuid import uuid4

from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.orchestrator.orchestrator import SupportOrchestrator
from ai_core.state.support_state import SupportState


class ChatService:

    def __init__(self):

        self.orchestrator = SupportOrchestrator()

    async def process(
        self,
        message: str,
        customer_id: str = "CUST-001",
        conversation_id: str = "CONV-001",
    ) -> SupportState:

        state = SupportState(

            request=CustomerRequest(
                message=message,
                customer_id=customer_id,
                conversation_id=conversation_id,
            ),

            metadata=ProcessingMetadata(
                request_id=str(uuid4()),
            ),
        )

        updated_state = await self.orchestrator.run(state)

        return updated_state