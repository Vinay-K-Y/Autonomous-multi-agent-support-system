from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.tool_call import ToolCall

import ai_core.tools

from ai_core.tools.executor import tool_executor


def test_execute_plan():

    plan = ExecutionPlan(
        reasoning="Refund request",
        tool_calls=[
            ToolCall(
                tool="ticket",
                parameters={
                    "priority": "high"
                },
            ),
            ToolCall(
                tool="memory",
                parameters={
                    "conversation_id": "demo"
                },
            ),
        ],
    )

    results = tool_executor.execute_plan(plan)

    print()

    print(results)

    assert "ticket" in results
    assert "memory" in results