from ai_core.agents.base_agent import BaseAgent
from ai_core.state.support_state import SupportState


class KnowledgeAgent(BaseAgent):

    async def execute(self, state: SupportState):

        state["retrieved_documents"] = [
            "Refund Policy",
            "Shipping Policy"
        ]

        return state