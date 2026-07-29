from ai_core.factories import SupportStateFactory


def test_support_state_factory():

    state = SupportStateFactory.create(
        message="My laptop is broken.",
        customer_id="CUST-001",
    )

    assert state.request.message == "My laptop is broken."
    assert state.request.customer_id == "CUST-001"

    assert state.metadata.request_id is not None
    assert state.request.conversation_id is not None
    