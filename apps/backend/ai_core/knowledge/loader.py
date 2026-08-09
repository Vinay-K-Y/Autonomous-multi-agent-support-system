from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader


class KnowledgeLoader:
    """
    Loads all markdown/text knowledge base files.
    """

    def __init__(self, knowledge_path: str = "knowledge_base"):
        self.knowledge_path = Path(knowledge_path)

    def load(self) -> list[Document]:

        documents = []

        for file in self.knowledge_path.glob("*.md"):

            loader = TextLoader(str(file), encoding="utf-8")

            docs = loader.load()
            
            # Add source metadata to each document
            for doc in docs:
                doc.metadata["source"] = file.name

            documents.extend(docs)

        return documents