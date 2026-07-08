from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document


class RetrieverService:
    """
    Retrieves the most relevant documents
    from the vector database.
    """

    def __init__(self, vector_store: VectorStore):
        self.retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 3,
                "fetch_k": 10,
            }
        )

    def retrieve(self, query: str) -> list[Document]:
        docs = self.retriever.invoke(query)
        
        # Deduplicate by content
        unique_docs = []
        seen = set()
        for doc in docs:
            if doc.page_content not in seen:
                unique_docs.append(doc)
                seen.add(doc.page_content)
        
        return unique_docs

    def search(self, query: str) -> list[Document]:
        return self.retrieve(query)