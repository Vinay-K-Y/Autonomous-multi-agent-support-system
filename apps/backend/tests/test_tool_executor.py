import pytest

from ai_core.agents.tool_executor import tool_executor_node
from ai_core.factories import SupportStateFactory
from ai_core.models.decision import DecisionResult
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.tool_call import ToolCall


def _approved_state(tool_name: str, parameters: dict):
    state = SupportStateFactory.create(
        message="I want to speak to a manager, this is unacceptable.",
        customer_id="CUST-001",
    )

    plan = ExecutionPlan(
        reasoning="test plan",
        tool_calls=[ToolCall(tool=tool_name, parameters=parameters)],
    )

    state.execution_plan = plan
    state.decision = DecisionResult(approved=True, reasoning="test approval")

    return state


@pytest.mark.asyncio
async def test_tool_executor_node_syncs_human_review_onto_state():
    state = _approved_state("human_review", {"reason": "customer is escalating"})

    result = await tool_executor_node(state)

    assert result.human_review.required is True
    assert result.human_review.reason == "customer is escalating"


@pytest.mark.asyncio
async def test_tool_executor_node_syncs_ticket_onto_state():
    state = _approved_state("ticket", {"priority": "high"})

    result = await tool_executor_node(state)

    assert result.ticket is not None
    assert result.ticket.ticket_required is True
    assert result.ticket.ticket_id is not None
    assert result.ticket.priority == "high"


@pytest.mark.asyncio
async def test_tool_executor_node_survives_bad_tool_call():
    # Unknown tool name should not crash the node or the request.
    state = _approved_state("not_a_real_tool", {})

    result = await tool_executor_node(state)

    assert result.human_review.required is False
    assert any(
        "tool execution failed" in reason
        for reason in result.metadata.routing_reasons
    )


@pytest.mark.asyncio
async def test_escalation_for_angry_customer():
    """Test that angry/frustrated customer messages trigger human review escalation."""
    from ai_core.models.intent import IntentOutput, IntentType
    from ai_core.workflow.decision_engine import DecisionEngine
    from ai_core.workflow.rules import WORKFLOW_RULES
    
    # Create state with angry customer message and low confidence intent
    state = SupportStateFactory.create(
        message="This is unacceptable, I want to speak to a manager immediately!",
        customer_id="CUST-002",
    )
    
    # Set low confidence intent to trigger escalation
    state.intent = IntentOutput(
        intent=IntentType.GENERAL,
        confidence=0.65,  # Below default threshold of 0.70
        reasoning="Customer is angry but intent is unclear"
    )
    
    # Create execution plan without human_review
    plan = ExecutionPlan(
        reasoning="Standard knowledge retrieval",
        tool_calls=[
            ToolCall(tool="knowledge", parameters={"question": state.request.message})
        ]
    )
    state.execution_plan = plan
    
    # Run decision engine evaluation
    decision_engine = DecisionEngine(rules=WORKFLOW_RULES)
    decision = decision_engine.evaluate(state)
    
    # Assert that human_review was added to the modified plan
    assert decision.modified_plan is not None
    has_human_review = any(
        tc.tool == "human_review" 
        for tc in decision.modified_plan.tool_calls
    )
    assert has_human_review, "Decision engine should add human_review for low confidence"