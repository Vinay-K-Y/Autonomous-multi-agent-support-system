from fastapi import APIRouter

from app.schemas.request import SupportRequest

from app.schemas.response import SupportResponse

from app.services.support_service import SupportService

router = APIRouter(
    prefix="/api/v1/support",
    tags=["Support"],
)

service = SupportService()


@router.post(
    "",
    response_model=SupportResponse,
)
def process_support_request(
    request: SupportRequest,
):

    return service.process_request(

        message=request.message,

        customer_id=request.customer_id,

        conversation_id=request.conversation_id,

        language=request.language,

        channel=request.channel,
    )