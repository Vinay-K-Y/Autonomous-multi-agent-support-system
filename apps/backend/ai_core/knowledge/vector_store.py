from langchain_community.vectorstores import FAISS


class VectorStoreService:

    def __init__(self):
        self.vector_store = None

    def build(self, documents, embedding_model):
        self.vector_store = FAISS.from_documents(
            documents,
            embedding_model
        )
        return self.vector_store

    def get(self):
        return self.vector_store