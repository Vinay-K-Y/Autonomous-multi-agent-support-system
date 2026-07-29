from fastapi import APIRouter, Request

from app.schemas.request import SupportRequest

from app.schemas.response import SupportResponse

from app.services.support_service import SupportService
from app.middleware.rate_limit import rate_limit_requests

router = APIRouter(
    prefix="/api/v1/support",
    tags=["Support"],
)

service = SupportService()


@router.post(
    "",
    response_model=SupportResponse,
)
@rate_limit_requests(requests=100, period=60)
def process_support_request(
    request: Request,
    support_request: SupportRequest,
):

    return service.process_request(

        message=support_request.message,

        customer_id=support_request.customer_id,

        conversation_id=support_request.conversation_id,

        language=support_request.language,

        channel=support_request.channel,
    )