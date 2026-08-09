from ai_core.rag.pipeline import RAGPipeline
from ai_core.tools.base_tool import BaseTool
from typing import Any


class KnowledgeTool(BaseTool):

    name = "knowledge"
    description = "Searches the company knowledge base."
    
    # Singleton RAGPipeline to avoid per-request initialization
    _rag_pipeline = None

    def __init__(self):
        if KnowledgeTool._rag_pipeline is None:
            KnowledgeTool._rag_pipeline = RAGPipeline()
        self.rag = KnowledgeTool._rag_pipeline

    def execute(
        self,
        question: str,
        conversation: str = "",
        state: Any = None,
    ):

        return self.rag.ask(
            question=question,
            conversation=conversation,
            state=state,
        )