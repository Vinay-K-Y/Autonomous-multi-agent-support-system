from app.schemas.response import SupportResponse

from app.services.workflow_executor import WorkflowExecutor


class SupportService:

    def __init__(self):

        self.executor = WorkflowExecutor()

    def process_request(

        self,

        message: str,

        customer_id: str | None = None,

        conversation_id: str | None = None,

        language: str = "en",

        channel: str = "web",
    ):

        state = self.executor.execute(

            message=message,

            customer_id=customer_id,

            conversation_id=conversation_id,

            language=language,

            channel=channel,
        )

        print("=" * 80)
        print("SupportService - Final state.response:")
        print(state.response)
        print()
        print("SupportService - state.response.response:")
        print(state.response.response if state.response else "state.response is None")
        print("=" * 80)

        return SupportResponse(

            conversation_id=state.request.conversation_id,

            response=state.response.response,

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
                state.ticket.ticket_id
                if state.ticket
                else (
                    state.tool_results.get("ticket").ticket_id
                    if state.tool_results and state.tool_results.get("ticket")
                    else None
                )
            ),

            requires_human_review=(
                state.human_review.required
            ),

            processing_time_ms=(
                state.metadata.processing_time_ms
            ),
        )