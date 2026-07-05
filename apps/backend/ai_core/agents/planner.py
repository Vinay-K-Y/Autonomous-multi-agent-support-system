from ai_core.planner.planner import PlannerAgent
from ai_core.state import SupportState


planner = PlannerAgent()


async def planner_node(
    state: SupportState,
) -> SupportState:

    plan = await planner.run(
        state.request.message
    )

    state.execution_plan = plan
    state.metadata.routing_reasons.append("planner completed")

    return state