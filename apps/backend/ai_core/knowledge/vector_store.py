from langchain_chroma import Chroma
import os


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
        # Load existing vector store from disk instead of rebuilding
        if os.path.exists("chroma_db"):
            return Chroma(
                persist_directory="chroma_db",
                embedding_function=embeddings,
            )
        # Fallback to building if doesn't exist
        return None