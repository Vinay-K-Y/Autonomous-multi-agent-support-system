from ai_core.graph.builder import route_after_intent
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.intent import IntentOutput, IntentType
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState


def _state(confidence: float, intent: IntentType, force_full_pipeline: bool = False) -> SupportState:
    state = SupportState(
        request=CustomerRequest(message="test message"),
        metadata=ProcessingMetadata(request_id="REQ-ROUTING-TEST"),
        force_full_pipeline=force_full_pipeline,
    )
    state.intent = IntentOutput(intent=intent, confidence=confidence, reasoning="test")
    return state


def test_high_confidence_general_query_skips_to_response_by_default():
    state = _state(confidence=0.9, intent=IntentType.GENERAL)
    assert route_after_intent(state) == "response"


def test_force_full_pipeline_overrides_the_skip_shortcut():
    # Same query that would normally skip straight to response — but with
    # force_full_pipeline=True it must still route through the planner.
    # This is exactly the override the benchmark script uses to get an
    # apples-to-apples "full pipeline" measurement for the same input.
    state = _state(confidence=0.9, intent=IntentType.GENERAL, force_full_pipeline=True)
    assert route_after_intent(state) == "planner"


def test_low_confidence_general_query_routes_to_planner_regardless():
    state = _state(confidence=0.5, intent=IntentType.GENERAL)
    assert route_after_intent(state) == "planner"


def test_non_general_intent_routes_to_planner_even_at_high_confidence():
    state = _state(confidence=0.95, intent=IntentType.REFUND)
    assert route_after_intent(state) == "planner"


def test_no_intent_routes_to_planner():
    state = SupportState(
        request=CustomerRequest(message="test message"),
        metadata=ProcessingMetadata(request_id="REQ-ROUTING-TEST-2"),
    )
    assert route_after_intent(state) == "planner"
