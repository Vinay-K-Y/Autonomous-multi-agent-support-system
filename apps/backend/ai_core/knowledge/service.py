from langchain_core.documents import Document

from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.retriever import RetrieverService
from ai_core.knowledge.vector_store import VectorStoreService


class KnowledgeService:
    """
    Singleton Knowledge Service.

    Loads and indexes the knowledge base only once.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if self._initialized:
            return

        print("Loading Knowledge Base...")

        loader = KnowledgeLoader()
        documents = loader.load()

        print(f"Loaded {len(documents)} documents")

        chunker = KnowledgeChunker()
        chunks = chunker.split(documents)

        print(f"Generated {len(chunks)} chunks")

        embedding = EmbeddingService().get()

        vector_store = VectorStoreService().build(
            chunks,
            embedding,
        )

        self.retriever = RetrieverService(vector_store)

        self._initialized = True

        print("Knowledge Service Ready!")

    def search(self, query: str) -> list[Document]:

        return self.retriever.retrieve(query)