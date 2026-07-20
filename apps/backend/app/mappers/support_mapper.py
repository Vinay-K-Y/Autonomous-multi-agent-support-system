from app.schemas.response import SupportResponse
from ai_core.state.support_state import SupportState


class SupportMapper:

    @staticmethod
    def to_response(state: SupportState) -> SupportResponse:

        ticket = state.ticket

        if ticket is None and state.tool_results:
            ticket = state.tool_results.get("ticket")

        return SupportResponse(

            conversation_id=state.request.conversation_id,

            response=(
                state.response.response
                if state.response
                else ""
            ),

            intent=(
                state.intent.intent.value
                if state.intent
                else None
            ),

            confidence=(
                state.response.confidence
                if state.response
                else 0
            ),

            ticket_id=(
                ticket.ticket_id
                if ticket
                else None
            ),

            requires_human_review=(
                state.human_review.required
                if state.human_review
                else False
            ),

            processing_time_ms=(
                state.metadata.processing_time_ms
            ),
        )