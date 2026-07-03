from ai_core.agents.intent_agent import IntentAgent
from ai_core.agents.knowledge_agent import KnowledgeAgent
from ai_core.agents.ticket_agent import TicketAgent
from ai_core.agents.response_agent import ResponseAgent
from ai_core.agents.human_review_agent import HumanReviewAgent


class AgentRegistry:
    """
    Registry that owns all agent instances.

    The orchestrator asks the registry for agents instead
    of creating them directly.
    """

    def __init__(self):

        self._agents = {
            "intent": IntentAgent(),
            "knowledge": KnowledgeAgent(),
            "ticket": TicketAgent(),
            "human_review": HumanReviewAgent(),
            "response": ResponseAgent(),
        }

    def get(self, name: str):

        if name not in self._agents:
            raise ValueError(f"Unknown agent: {name}")

        return self._agents[name]