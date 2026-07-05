from langchain_chroma import Chroma


class VectorStoreService:

    def build(
        self,
        documents,
        embeddings,
    ):

        return Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="chroma_db",
        )

    def load(
        self,
        embeddings,
    ):

        return Chroma(
            persist_directory="chroma_db",
            embedding_function=embeddings,
        )