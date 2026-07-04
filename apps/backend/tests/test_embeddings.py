from ai_core.knowledge.embeddings import EmbeddingService


def test_embeddings():

    embedding = EmbeddingService().get()

    vector = embedding.embed_query(
        "My laptop is damaged"
    )

    print(f"Vector length: {len(vector)}")
    print(vector[:10])

    assert len(vector) > 0