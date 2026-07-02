from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

service = ChatService()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):

    state = await service.process(request.message)

    return ChatResponse(
         intent=state["intent"],
        confidence=state["confidence"],
        ticket_required=state["ticket_required"],
        ticket_id=state["ticket_id"],
        response=state["final_response"],
        escalation_required=state["escalation_required"],
    )