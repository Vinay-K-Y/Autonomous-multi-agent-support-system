from ai_core.rag.pipeline import RAGPipeline


def test_rag_answer():

    rag = RAGPipeline()

    answer = rag.ask(
        "How can I get a refund?"
    )

    print("\nAnswer:\n")
    print(answer)

    assert answer is not None
    assert len(answer) > 0