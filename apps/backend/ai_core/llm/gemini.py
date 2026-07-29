from typing import Type
import asyncio
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.config import settings
from ai_core.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        # Avoid creating a live client when API keys are not configured
        # (this can otherwise hang during network attempts in tests).
        self.model = None
        if getattr(settings, "GOOGLE_API_KEY", None):
            self.model = ChatGoogleGenerativeAI(
                model=settings.MODEL_NAME,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.TEMPERATURE,
            )

    async def generate(
        self,
        prompt: str,
    ) -> str:
        try:
            if self.model is None:
                raise RuntimeError("GOOGLE_API_KEY not configured")
            response = await self.model.ainvoke(prompt)
            return getattr(response, "content", str(response))
        except Exception:
            return "I’m unable to reach the language model right now, but I can still help."

    async def generate_structured(
        self,
        prompt: ChatPromptTemplate,
        output_schema: Type[BaseModel],
        variables: dict,
    ):
        if self.model is None:
            # Let LLMService handle typed fallbacks for specific schemas.
            raise RuntimeError("GOOGLE_API_KEY not configured")
        structured_model = self.model.with_structured_output(output_schema)

        chain = prompt | structured_model

        # Configurable timeout: longer for runtime, short under pytest to avoid hangs.
        timeout = getattr(settings, "LLM_TIMEOUT_SECONDS", 30.0)
        if os.getenv("PYTEST_CURRENT_TEST"):
            timeout = getattr(settings, "LLM_TEST_TIMEOUT_SECONDS", 8.0)
        response = await asyncio.wait_for(chain.ainvoke(variables), timeout=timeout)

        return response