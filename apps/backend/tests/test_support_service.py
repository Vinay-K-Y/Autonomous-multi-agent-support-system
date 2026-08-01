import asyncio
from app.schemas.request import SupportRequest
from app.services.support_service import SupportService


async def test_support_service():

    service = SupportService()

    result = await service.process_request(

        message="How do I get a refund?"
    )

    assert result.response is not None

    print(result)


def test_support_service_sync():
    """Sync wrapper for async test"""
    asyncio.run(test_support_service())