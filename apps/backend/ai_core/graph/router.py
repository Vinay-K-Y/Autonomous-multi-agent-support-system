from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine

engine = DecisionEngine()


def route_after_intent(state: SupportState) -> str:
    return engine.route_after_intent(state)