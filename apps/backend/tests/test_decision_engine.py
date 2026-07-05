from ai_core.models.customer_request import CustomerRequest
from ai_core.models.intent import IntentOutput, IntentType
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine


def build_state(intent: IntentType | None = None, confidence: float = 0.95) -> SupportState:
    state = SupportState(
        request=CustomerRequest(message="How do I get a refund?"),
        metadata=ProcessingMetadata(request_id="REQ-DECISION"),
    )

    if intent is not None:
        state.intent = IntentOutput(intent=intent, confidence=confidence, reasoning="test")

    return state


def test_decision_engine_retrieves_knowledge_for_refund_requests() -> None:
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND)

    should_retrieve, reason = engine.should_retrieve_knowledge(state)

    assert should_retrieve is True
    assert "knowledge" in reason.lower()


def test_decision_engine_creates_tickets_for_refund_requests() -> None:
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND)

    should_create, reason = engine.should_create_ticket(state)

    assert should_create is True
    assert "ticket" in reason.lower()


def test_decision_engine_escalates_low_confidence_requests() -> None:
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND, confidence=0.6)

    should_escalate, reason = engine.should_escalate(state)

    assert should_escalate is True
    assert "escalat" in reason.lower()


def test_decision_engine_routes_refunds_to_ticket_flow() -> None:
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND)

    route = engine.route_after_intent(state)

    assert route == "ticket"
    assert state.metadata.routing_reasons
