from ai_core.knowledge.loader import KnowledgeLoader
from ai_core.knowledge.chunker import KnowledgeChunker


def test_chunker():

    loader = KnowledgeLoader("knowledge_base")

    documents = loader.load()

    chunker = KnowledgeChunker()

    chunks = chunker.split(documents)

    assert len(chunks) > 0

    print(f"\nLoaded {len(documents)} documents")
    print(f"Generated {len(chunks)} chunks\n")

    print(chunks[0].page_content)