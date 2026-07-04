from ai_core.knowledge.instance import knowledge_service


def test_instance():

    docs = knowledge_service.search("refund")

    assert len(docs) > 0

    print()

    print("Retrieved:")

    for doc in docs:
        print("-" * 40)
        print(doc.page_content)