import time
import uuid

from ai_core.graph import support_graph

from ai_core.state.support_state import SupportState

from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.graph import invoke_sync

class WorkflowExecutor:

    def execute(
        self,
        message: str,
        customer_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
        channel: str = "web",
    ):

        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        state = SupportState(

            request=CustomerRequest(
                message=message,
                customer_id=customer_id,
                conversation_id=conversation_id,
                language=language,
                channel=channel,
            ),

            metadata=ProcessingMetadata(
                request_id=str(uuid.uuid4()),
            ),
        )

        start = time.perf_counter()

        result = invoke_sync(state)

        elapsed = (time.perf_counter() - start) * 1000

        result.metadata.processing_time_ms = elapsed

        return result