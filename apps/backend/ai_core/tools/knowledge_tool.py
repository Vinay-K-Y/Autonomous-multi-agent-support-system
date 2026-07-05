from ai_core.rag.pipeline import RAGPipeline
from ai_core.tools.base_tool import BaseTool


class KnowledgeTool(BaseTool):

    name = "knowledge"
    description = "Searches the company knowledge base."
    
    def __init__(self):

        self.rag = RAGPipeline()

    def execute(
        self,
        question: str,
        conversation: str = "",
    ):

        return self.rag.ask(
            question=question,
            conversation=conversation,
        )