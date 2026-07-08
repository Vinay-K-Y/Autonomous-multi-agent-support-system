from ai_core.observability.decorators import traced
from ai_core.planner.planner import PlannerAgent
from ai_core.state.support_state import SupportState


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

    return state