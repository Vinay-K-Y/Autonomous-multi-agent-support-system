from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

service = ChatService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):

    state = await service.process(
        message=request.message,
    )

    return ChatResponse(
        intent=state.intent.intent.value if state.intent else "",
        confidence=state.intent.confidence if state.intent else 0.0,

        ticket_required=(
            state.ticket.ticket_required
            if state.ticket
            else False
        ),

        ticket_id=(
            state.ticket.ticket_id
            if state.ticket
            else None
        ),

        response=(
            state.response.response
            if state.response
            else ""
        ),

        escalation_required=(
            state.human_review.required
            if state.human_review
            else False
        ),
    )