from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.vector_store import VectorStoreService
from ai_core.knowledge.retriever import RetrieverService


def test_retriever():

    loader = KnowledgeLoader()
    docs = loader.load()

    chunker = KnowledgeChunker()
    chunks = chunker.split(docs)

    embedding = EmbeddingService().get()

    store = VectorStoreService().build(
        chunks,
        embedding,
    )

    retriever = RetrieverService(store)

    results = retriever.retrieve(
        "How can I cancel my order?"
    )

    assert len(results) > 0

    print("\nRetrieved Documents:\n")

    for doc in results:
        print(doc.page_content)
        print("-" * 50)