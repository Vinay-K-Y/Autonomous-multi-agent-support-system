from ai_core.knowledge.service import KnowledgeService


def test_knowledge_service():

    service = KnowledgeService()

    results = service.search(
        "Can I cancel my order?"
    )

    assert len(results) > 0

    print("\nRetrieved Documents:\n")

    for doc in results:
        print(doc.page_content)
        print("-" * 60)