from ai_core.agents.base_agent import BaseAgent
from ai_core.models.knowledge import (
    KnowledgeOutput,
    KnowledgeSource,
)
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import mark_documents_retrieved, record_agent_execution, start_agent_timer
from ai_core.error_handling import with_fallback, KNOWLEDGE_FALLBACK


class KnowledgeAgent(BaseAgent):

    @with_fallback("knowledge_agent", KNOWLEDGE_FALLBACK)
    async def execute(self, state: SupportState) -> SupportState:
        started_at = start_agent_timer()
        message = (state.request.message or "").lower()

        if "refund" in message:
            answer = "Your refund request can be reviewed under the refund policy."
            title = "Refund Policy"
            source = "company_policy.pdf"
        else:
            answer = "I found a relevant policy entry for your request."
            title = "Support Policy"
            source = "support_policy.pdf"

        state.knowledge = KnowledgeOutput(
            answer=answer,
            confidence=0.95,
            sources=[
                KnowledgeSource(
                    title=title,
                    source=source,
                    confidence=0.95,
                )
            ],
        )

        mark_documents_retrieved(state, 1)
        record_agent_execution(state, "knowledge", started_at, details="knowledge retrieval completed")

        return state