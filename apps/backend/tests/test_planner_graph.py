from ai_core.state import SupportState

from ai_core.models.customer_request import CustomerRequest

from ai_core.models.metadata import ProcessingMetadata

from ai_core.graph import support_graph


def test_planner_graph():

    state = SupportState(

        request=CustomerRequest(

            message="How do I get a refund?"

        ),

        metadata=ProcessingMetadata(

            request_id="REQ-001"

        ),

    )

    result = support_graph.invoke(
        state
    )

    assert result.execution_plan is not None

    assert len(
        result.execution_plan.tool_calls
    ) > 0

    assert len(
        result.tool_results
    ) > 0