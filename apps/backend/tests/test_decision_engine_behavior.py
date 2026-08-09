from ai_core.models.customer_request import CustomerRequest
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.intent import IntentOutput, IntentType
from ai_core.models.metadata import ProcessingMetadata
from ai_core.models.tool_call import ToolCall
from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine


def build_state(intent: IntentType | None = None, confidence: float = 0.95) -> SupportState:
    state = SupportState(
        request=CustomerRequest(message="How do I get a refund?"),
        metadata=ProcessingMetadata(request_id="REQ-DECISION-BEHAVIOR"),
    )

    if intent is not None:
        state.intent = IntentOutput(intent=intent, confidence=confidence, reasoning="test")

    return state


def test_decision_engine_adds_ticket_for_high_confidence_refund() -> None:
    """Given REFUND intent with confidence=0.9, assert plan includes ticket tool."""
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND, confidence=0.9)
    
    # Set up an initial execution plan
    state.execution_plan = ExecutionPlan(
        reasoning="Initial plan",
        tool_calls=[]
    )
    
    result = engine.evaluate(state)
    
    # Assert that ticket tool is in the modified plan
    ticket_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "ticket"]
    assert len(ticket_tools) == 1, f"Expected 1 ticket tool, got {len(ticket_tools)}"
    assert ticket_tools[0].parameters.get("priority") == "medium"


def test_decision_engine_adds_human_review_for_low_confidence_technical() -> None:
    """Given TECHNICAL_ISSUE with confidence=0.5 (below escalation_threshold), assert both ticket and human_review."""
    engine = DecisionEngine()
    state = build_state(IntentType.TECHNICAL_ISSUE, confidence=0.5)
    
    # Set up an initial execution plan
    state.execution_plan = ExecutionPlan(
        reasoning="Initial plan",
        tool_calls=[]
    )
    
    result = engine.evaluate(state)
    
    # Assert that both ticket and human_review tools are in the modified plan
    ticket_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "ticket"]
    human_review_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "human_review"]
    
    assert len(ticket_tools) == 1, f"Expected 1 ticket tool, got {len(ticket_tools)}"
    assert len(human_review_tools) == 1, f"Expected 1 human_review tool, got {len(human_review_tools)}"
    assert "escalat" in human_review_tools[0].parameters.get("reason", "").lower()


def test_decision_engine_blocks_ticket_for_high_confidence_general() -> None:
    """Given GENERAL intent with confidence=0.9, assert ticket is blocked if in original plan."""
    engine = DecisionEngine()
    state = build_state(IntentType.GENERAL, confidence=0.9)
    
    # Set up an initial execution plan with a ticket tool
    state.execution_plan = ExecutionPlan(
        reasoning="Initial plan with ticket",
        tool_calls=[
            ToolCall(tool="ticket", parameters={"priority": "medium"}),
            ToolCall(tool="knowledge", parameters={"question": "test"})
        ]
    )
    
    result = engine.evaluate(state)
    
    # Assert that ticket is NOT in the modified plan
    ticket_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "ticket"]
    assert len(ticket_tools) == 0, f"Expected 0 ticket tools, got {len(ticket_tools)}"
    
    # Assert that ticket appears in blocked_tools
    assert "ticket" in result.blocked_tools, f"Expected 'ticket' in blocked_tools, got {result.blocked_tools}"


def test_decision_engine_adds_knowledge_for_refund() -> None:
    """Given REFUND intent, assert knowledge tool is added."""
    engine = DecisionEngine()
    state = build_state(IntentType.REFUND, confidence=0.9)
    
    # Set up an initial execution plan
    state.execution_plan = ExecutionPlan(
        reasoning="Initial plan",
        tool_calls=[]
    )
    
    result = engine.evaluate(state)
    
    # Assert that knowledge tool is in the modified plan
    knowledge_tools = [tc for tc in result.modified_plan.tool_calls if tc.tool == "knowledge"]
    assert len(knowledge_tools) == 1, f"Expected 1 knowledge tool, got {len(knowledge_tools)}"
