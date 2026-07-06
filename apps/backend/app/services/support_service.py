import uuid

from ai_core.graph.builder import support_graph

from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState

from app.schemas.request import SupportRequest
from app.schemas.response import SupportResponse, TicketResponse


class SupportService:
    """
    Main entry point for all customer support requests.

    Converts API DTOs into SupportState,
    executes the LangGraph workflow,
    converts the result back into API DTOs.
    """

    def process(self, request: SupportRequest) -> SupportResponse:

        workflow_id = str(uuid.uuid4())

        conversation_id = (
            request.conversation_id
            or str(uuid.uuid4())
        )

        state = SupportState(

            request=CustomerRequest(

                message=request.message,

                customer_id=request.customer_id,

                conversation_id=conversation_id,

                language=request.language,

                channel=request.channel,

                metadata=request.metadata,
            ),

            metadata=ProcessingMetadata(

                request_id=workflow_id,
            ),
        )

        result = support_graph.invoke(state)

        ticket = None

        if result.ticket:

            ticket = TicketResponse(

                ticket_required=result.ticket.ticket_required,

                ticket_id=result.ticket.ticket_id,

                priority=result.ticket.priority,

                assigned_team=result.ticket.assigned_team,
            )

        return SupportResponse(

            workflow_id=workflow_id,

            conversation_id=conversation_id,

            response=result.response.response,

            confidence=result.response.confidence,

            intent=(
                result.intent.intent.value
                if result.intent
                else None
            ),

            ticket=ticket,

            planner_used=result.execution_plan is not None,

            knowledge_used="knowledge" in result.tool_results,

            human_review_required=result.human_review.required,
        )