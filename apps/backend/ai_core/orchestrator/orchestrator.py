from ai_core.agents.intent_agent import IntentAgent
from ai_core.agents.knowledge_agent import KnowledgeAgent
from ai_core.agents.ticket_agent import TicketAgent
from ai_core.agents.response_agent import ResponseAgent
from ai_core.agents.human_review_agent import HumanReviewAgent

from ai_core.state.support_state import SupportState


class SupportOrchestrator:

    def __init__(self):

        self.intent = IntentAgent()
        self.knowledge = KnowledgeAgent()
        self.ticket = TicketAgent()
        self.response = ResponseAgent()
        self.review = HumanReviewAgent()

    async def run(self, state: SupportState):

        state = await self.intent.execute(state)

        state = await self.knowledge.execute(state)

        state = await self.ticket.execute(state)

        state = await self.response.execute(state)

        state = await self.review.execute(state)

        return state