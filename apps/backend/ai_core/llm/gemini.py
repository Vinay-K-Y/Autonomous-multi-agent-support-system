from typing import Type

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.config import settings
from ai_core.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self):

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

        structured_model = self.model.with_structured_output(output_schema)

        chain = prompt | structured_model

        response = await chain.ainvoke(variables)

        return response