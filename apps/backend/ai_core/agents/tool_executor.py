from ai_core.state import SupportState

from ai_core.tools.executor import tool_executor


def tool_executor_node(
    state: SupportState,
) -> SupportState:

    if state.execution_plan is None:
        return state

    results = tool_executor.execute_plan(
        state.execution_plan
    )

    state.tool_results = results
    state.metadata.routing_reasons.append("tools executed")

    return state