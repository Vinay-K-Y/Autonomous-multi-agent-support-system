from app.core.config import settings

from ai_core.llm.gemini import GeminiProvider


class LLMFactory:

    @staticmethod
    def create():

        provider = settings.LLM_PROVIDER.lower()

        if provider == "gemini":
            return GeminiProvider()

        raise ValueError(f"Unsupported LLM provider: {provider}")