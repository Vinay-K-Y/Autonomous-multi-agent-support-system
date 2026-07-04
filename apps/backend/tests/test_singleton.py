from ai_core.knowledge.service import KnowledgeService


def test_singleton():

    service1 = KnowledgeService()

    service2 = KnowledgeService()

    assert service1 is service2

    print(id(service1))
    print(id(service2))