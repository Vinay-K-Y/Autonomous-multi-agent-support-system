from typing import Type
import asyncio
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.config import settings
from ai_core.llm.base import BaseLLMProvider


class OpenAILocalProvider(BaseLLMProvider):

    def __init__(self):
        # Initialize OpenAI client pointing to local endpoint
        self.model = None
        if getattr(settings, "OPENAI_BASE_URL", None):
            self.model = ChatOpenAI(
                model=settings.MODEL_NAME,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                temperature=settings.TEMPERATURE,
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )

    async def generate(
        self,
        prompt: str,
    ) -> str:
        try:
            if self.model is None:
                raise RuntimeError("OPENAI_BASE_URL not configured")
            response = await self.model.ainvoke(prompt)
            return getattr(response, "content", str(response))
        except Exception:
            return "I'm unable to reach the language model right now, but I can still help."

    async def generate_structured(
        self,
        prompt: ChatPromptTemplate,
        output_schema: Type[BaseModel],
        variables: dict,
    ):
        if self.model is None:
            raise RuntimeError("OPENAI_BASE_URL not configured")
        
        structured_model = self.model.with_structured_output(output_schema)
        chain = prompt | structured_model

        # Configurable timeout: longer for runtime, short under pytest to avoid hangs.
        timeout = getattr(settings, "LLM_TIMEOUT_SECONDS", 60.0)
        if os.getenv("PYTEST_CURRENT_TEST"):
            timeout = getattr(settings, "LLM_TEST_TIMEOUT_SECONDS", 15.0)
        
        response = await asyncio.wait_for(chain.ainvoke(variables), timeout=timeout)
        return response
