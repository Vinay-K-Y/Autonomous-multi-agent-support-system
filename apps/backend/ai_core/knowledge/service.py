from langchain_core.documents import Document

from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.retriever import RetrieverService
from ai_core.knowledge.vector_store import VectorStoreService


class KnowledgeService:
    """
    Complete RAG pipeline.

    Loads the knowledge base, creates embeddings,
    builds the vector store, and exposes a search API.
    """

    def __init__(self):

        loader = KnowledgeLoader()
        documents = loader.load()

        chunker = KnowledgeChunker()
        chunks = chunker.split(documents)

        embedding = EmbeddingService().get()

        vector_store = VectorStoreService().build(
            chunks,
            embedding,
        )

        self.retriever = RetrieverService(vector_store)

    def search(self, query: str) -> list[Document]:
        return self.retriever.retrieve(query)