from app.schemas.request import SupportRequest
from app.services.support_service import SupportService


def test_support_service():

    service = SupportService()

    result = service.process_request(

        message="How do I get a refund?"
    )

    assert result.response is not None

    print(result)