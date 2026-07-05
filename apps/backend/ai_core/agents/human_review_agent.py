from ai_core.agents.base_agent import BaseAgent
from ai_core.models.human_review import HumanReview
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import record_agent_execution, start_agent_timer


class HumanReviewAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()

        if (
            state.intent is not None
            and state.intent.confidence < 0.70
        ):

            state.human_review = HumanReview(
                required=True,
                reason="Low confidence intent detection.",
            )

        else:

            state.human_review = HumanReview(
                required=False,
            )

        record_agent_execution(state, "human_review", started_at, details="human review decision completed")
        return state