from ai_core.observability.decorators import traced
from ai_core.planner.planner import PlannerAgent
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import record_llm_fallback, increment_llm_calls


planner = PlannerAgent()


@traced("planner")
async def planner_node(
    state: SupportState,
) -> SupportState:

    plan = await planner.run(
        state.request.message
    )

    state.execution_plan = plan
    state.metadata.planner_reasoning = plan.reasoning
    state.metadata.routing_reasons.append("planner completed")

    if plan.used_fallback:
        record_llm_fallback(state, "planner")
    else:
        increment_llm_calls(state)

    return state