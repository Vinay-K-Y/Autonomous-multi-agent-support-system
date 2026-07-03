from ai_core.agents.base_agent import BaseAgent
from ai_core.models.human_review import HumanReview
from ai_core.state.support_state import SupportState


class HumanReviewAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

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

        return state