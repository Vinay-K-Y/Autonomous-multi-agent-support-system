from ai_core.agents.base_agent import BaseAgent
from ai_core.models.knowledge import (
    KnowledgeOutput,
    KnowledgeSource,
)
from ai_core.state.support_state import SupportState


class KnowledgeAgent(BaseAgent):

    async def execute(self, state: SupportState) -> SupportState:

        state.knowledge = KnowledgeOutput(
            answer="Relevant refund policy found.",
            confidence=0.95,
            sources=[
                KnowledgeSource(
                    title="Refund Policy",
                    source="company_policy.pdf",
                    confidence=0.95,
                )
            ],
        )

        return state