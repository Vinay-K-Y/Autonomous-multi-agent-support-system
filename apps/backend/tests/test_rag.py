from ai_core.rag.pipeline import RAGPipeline


def test_rag():

    rag = RAGPipeline()

    docs = rag.search(
        "How can I get a refund?"
    )

    print()

    for doc in docs:

        print(doc.page_content)
        print("-" * 50)

    assert len(docs) > 0