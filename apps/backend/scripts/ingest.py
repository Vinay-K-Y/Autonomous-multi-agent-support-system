from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.chunker import KnowledgeChunker
from ai_core.knowledge.embeddings import EmbeddingService
from ai_core.knowledge.vector_store import VectorStoreService


loader = KnowledgeLoader()
docs = loader.load()

chunker = KnowledgeChunker()
chunks = chunker.split(docs)

embeddings = EmbeddingService().get()

VectorStoreService().build(
    chunks,
    embeddings,
)

print("Knowledge base indexed successfully!")