import pytest

from ai_core.graph.builder import support_graph
from ai_core.state.support_state import SupportState
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata


@pytest.mark.asyncio
async def test_graph_execution():

    state = SupportState(
        request=CustomerRequest(
            message="How do I get a refund?"
        ),
        metadata=ProcessingMetadata(
            request_id="REQ-001"
        ),
    )

    result = await support_graph.ainvoke(state)

    print(result)

    assert result is not None
    assert result.execution_plan is not None
    assert result.decision is not None
    assert result.decision.approved
    assert result.tool_results is not None