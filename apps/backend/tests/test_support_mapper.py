from ai_core.factories import SupportStateFactory
from app.mappers import SupportMapper


def test_mapper():

    state = SupportStateFactory.create(
        message="Refund please"
    )

    response = SupportMapper.to_response(state)

    assert response.conversation_id == state.request.conversation_id
    