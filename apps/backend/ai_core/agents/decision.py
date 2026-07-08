from ai_core.observability.decorators import traced
from ai_core.workflow.decision_engine import DecisionEngine
from ai_core.state.support_state import SupportState

engine = DecisionEngine()


@traced("decision")
async def decision_node(
    state: SupportState,
) -> SupportState:

    decision = engine.evaluate(state)

    state.decision = decision

    state.metadata.decision_reasoning = decision.reasoning
    state.metadata.blocked_tools = decision.blocked_tools

    return state