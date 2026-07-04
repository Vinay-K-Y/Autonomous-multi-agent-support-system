from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document


class RetrieverService:
    """
    Retrieves the most relevant documents
    from the vector database.
    """

    def __init__(self, vector_store: VectorStore):
        self.retriever = vector_store.as_retriever(
            search_kwargs={"k": 3}
        )

    def retrieve(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)