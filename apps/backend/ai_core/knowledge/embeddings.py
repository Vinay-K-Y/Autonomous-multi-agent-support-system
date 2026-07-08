from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

EMBEDDING_MODEL = "models/gemini-embedding-2"

class EmbeddingService:
    _embeddings = None

    def __init__(self):
        if EmbeddingService._embeddings is None:
            EmbeddingService._embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
            )

    def get(self):
        return EmbeddingService._embeddings