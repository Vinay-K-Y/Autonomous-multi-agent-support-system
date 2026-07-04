from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.vector_store import VectorStoreService


def test_vector_store():

    loader = KnowledgeLoader()
    docs = loader.load()

    chunker = KnowledgeChunker()
    chunks = chunker.split(docs)

    embedding = EmbeddingService().get()

    store = VectorStoreService().build(
        chunks,
        embedding,
    )

    assert store is not None

    print("Vector Store Created Successfully!")