from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

EMBEDDING_MODEL = "models/gemini-embedding-2"

class EmbeddingService:
    _embeddings = None

    def __init__(self):
        if EmbeddingService._embeddings is None:
            provider = settings.LLM_PROVIDER.lower()
            if provider == "gemini":
                EmbeddingService._embeddings = GoogleGenerativeAIEmbeddings(
                    model=EMBEDDING_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                )
            elif provider == "openai":
                # Local OpenAI-compatible endpoints typically don't have embedding models
                # Disable knowledge base search when using local LLM
                print("Note: Embeddings disabled for local OpenAI provider")
                print("Knowledge base search will not be available")
                EmbeddingService._embeddings = None
            else:
                raise ValueError(f"Unsupported LLM provider for embeddings: {provider}")

    def get(self):
        return EmbeddingService._embeddings