from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from ai_core.llm.factory import LLMFactory


class LLMService:

    def __init__(self):
        self.provider = LLMFactory.create()

    def get(self):
        return self.provider.model

    async def generate_structured(
        self,
        prompt: ChatPromptTemplate,
        output_schema: Type[BaseModel],
        variables: dict,
    ):
        return await self.provider.generate_structured(
            prompt=prompt,
            output_schema=output_schema,
            variables=variables,
        )


llm_service = LLMService()