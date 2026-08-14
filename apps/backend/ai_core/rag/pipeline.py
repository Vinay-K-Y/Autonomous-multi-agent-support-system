from langchain_core.exceptions import OutputParserException

from ai_core.knowledge.service import KnowledgeService
from ai_core.llm.service import LLMService
from ai_core.prompts.rag_prompt import RAG_PROMPT
from ai_core.state.support_state import SupportState
from ai_core.workflow.execution_trace import increment_llm_calls


class RAGPipeline:

    def __init__(self):
        # Use singleton KnowledgeService to avoid reloading on each request
        self.knowledge_service = KnowledgeService()
        self.llm = LLMService().get()

    def search(self, query: str):
        return self.knowledge_service.search(query)

    def ask(self, question: str, conversation: str = "", state: SupportState | None = None):

        context = self.get_context(question)

        prompt = RAG_PROMPT.format(
            conversation=conversation,
            context=context,
            question=question,
        )

        try:
            response = self.llm.invoke(prompt)
            if state:
                increment_llm_calls(state)
            return response.content
        except Exception:
            if state:
                from ai_core.workflow.execution_trace import record_llm_fallback
                record_llm_fallback(state, "rag_pipeline")
            if context:
                return (
                    "I found relevant information in the knowledge base. "
                    f"Here is the most relevant context:\n{context}"
                )
            return "I'm unable to reach the language model right now, but I can still help based on the available knowledge base."

    def get_context(self, query: str) -> str:

        docs = self.search(query)

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )