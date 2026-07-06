from ai_core.state import SupportState

from ai_core.tools.executor import tool_executor


def tool_executor_node(
    state: SupportState,
) -> SupportState:

    if state.execution_plan is None:
        return state

    if state.decision is None:
        return state

    if not state.decision.approved:
        return state

    plan = state.decision.modified_plan or state.execution_plan

    results = tool_executor.execute_plan(plan)

    state.tool_results = results
    state.metadata.routing_reasons.append("tools executed")

    return state