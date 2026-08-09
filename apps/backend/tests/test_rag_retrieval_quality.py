from ai_core.knowledge.service import KnowledgeService


def test_rag_retrieves_faq_for_contact_question() -> None:
    """Test that a question about contacting support retrieves faq.md content."""
    service = KnowledgeService()
    
    # Question clearly tied to faq.md
    question = "How do I contact support?"
    
    docs = service.search(question)
    
    # Assert we got results
    assert len(docs) > 0, "Expected at least one document to be retrieved"
    
    # Assert that faq.md appears in the top-3 retrieved chunks
    top_3_sources = [doc.metadata.get("source", "") for doc in docs[:3]]
    assert "faq.md" in top_3_sources, f"Expected 'faq.md' in top-3 sources, got {top_3_sources}"
    
    # Assert the content is relevant
    relevant_content = any("support@example.com" in doc.page_content for doc in docs[:3])
    assert relevant_content, "Expected email address in retrieved content"


def test_rag_retrieves_refund_policy_for_refund_question() -> None:
    """Test that a question about refund policy retrieves refund_policy.md content."""
    service = KnowledgeService()
    
    # Question clearly tied to refund_policy.md
    question = "How long do I have to request a refund?"
    
    docs = service.search(question)
    
    # Assert we got results
    assert len(docs) > 0, "Expected at least one document to be retrieved"
    
    # Assert that refund_policy.md appears in the top-3 retrieved chunks
    top_3_sources = [doc.metadata.get("source", "") for doc in docs[:3]]
    assert "refund_policy.md" in top_3_sources, f"Expected 'refund_policy.md' in top-3 sources, got {top_3_sources}"
    
    # Assert the content mentions 30 days
    relevant_content = any("30 days" in doc.page_content for doc in docs[:3])
    assert relevant_content, "Expected '30 days' in retrieved content"


def test_rag_retrieves_shipping_policy_for_shipping_question() -> None:
    """Test that a question about shipping retrieves shipping_policy.md content."""
    service = KnowledgeService()
    
    # Question clearly tied to shipping_policy.md
    question = "What are your shipping options?"
    
    docs = service.search(question)
    
    # Assert we got results
    assert len(docs) > 0, "Expected at least one document to be retrieved"
    
    # Assert that shipping_policy.md appears in the top-3 retrieved chunks
    top_3_sources = [doc.metadata.get("source", "") for doc in docs[:3]]
    assert "shipping_policy.md" in top_3_sources, f"Expected 'shipping_policy.md' in top-3 sources, got {top_3_sources}"


def test_rag_retrieves_warranty_policy_for_warranty_question() -> None:
    """Test that a question about warranty retrieves warrenty_policy.md content."""
    service = KnowledgeService()
    
    # Question clearly tied to warrenty_policy.md
    question = "What is covered under warranty?"
    
    docs = service.search(question)
    
    # Assert we got results
    assert len(docs) > 0, "Expected at least one document to be retrieved"
    
    # Assert that warrenty_policy.md appears in the top-3 retrieved chunks
    top_3_sources = [doc.metadata.get("source", "") for doc in docs[:3]]
    assert "warrenty_policy.md" in top_3_sources, f"Expected 'warrenty_policy.md' in top-3 sources, got {top_3_sources}"
