from ai_core.graph import support_graph
from ai_core.state import SupportState

from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata


def test_workflow_trace():

    state = SupportState(
        request=CustomerRequest(
            message="How do I get a refund?"
        ),
        metadata=ProcessingMetadata(
            request_id="TRACE-001"
        ),
    )

    result = support_graph.invoke(state)

    assert result.trace is not None

    assert len(result.trace.traces) > 0

    assert result.trace.total_duration_ms > 0

    print()

    print("Workflow Trace")

    print("----------------------")

    for step in result.trace.traces:

        print(step.agent, step.duration_ms)