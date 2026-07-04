from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

EMBEDDING_MODEL = "models/gemini-embedding-2"

class EmbeddingService:

    def __init__(self):

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )

    def get(self):
        return self.embeddings