from app.core.config import settings

from ai_core.llm.gemini import GeminiProvider
from ai_core.llm.openai_local import OpenAILocalProvider


class LLMFactory:
    _provider = None

    @staticmethod
    def create():
        if LLMFactory._provider is None:
            provider = settings.LLM_PROVIDER.lower()
            if provider == "gemini":
                LLMFactory._provider = GeminiProvider()
            elif provider == "openai":
                LLMFactory._provider = OpenAILocalProvider()
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        return LLMFactory._provider