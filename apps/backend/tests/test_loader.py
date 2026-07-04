from ai_core.knowledge.loader import KnowledgeLoader


def test_loader():

    loader = KnowledgeLoader()

    docs = loader.load()

    assert len(docs) >= 3

    for doc in docs:
        print("=" * 50)
        print(doc.page_content)