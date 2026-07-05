from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.vector_store import VectorStoreService
from ai_core.knowledge.retriever import RetrieverService
from ai_core.llm.service import LLMService
from ai_core.prompts.rag_prompt import RAG_PROMPT


class RAGPipeline:

    def __init__(self):

        loader = KnowledgeLoader()
        docs = loader.load()

        chunker = KnowledgeChunker()
        chunks = chunker.split(docs)

        embedding = EmbeddingService().get()

        store = VectorStoreService().build(
            chunks,
            embedding,
        )

        self.retriever = RetrieverService(store)
        self.llm = LLMService().get()

    def search(self, query: str):

        return self.retriever.search(query)

    def ask(self, question: str, conversation: str = ""):

        context = self.get_context(question)

        prompt = RAG_PROMPT.format(
            conversation=conversation,
            context=context,
            question=question,
        )

        response = self.llm.invoke(prompt)

        return response.content

    def get_context(self, query: str) -> str:

        docs = self.search(query)

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )