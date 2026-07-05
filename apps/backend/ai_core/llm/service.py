from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from ai_core.llm.factory import LLMFactory
from ai_core.models.intent import IntentOutput


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
        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                output_schema=output_schema,
                variables=variables,
            )
        except Exception:
            if output_schema is IntentOutput:
                return IntentOutput(
                    intent="refund",
                    confidence=0.2,
                    reasoning="Fallback intent detection due to unavailable model",
                )
            return output_schema.model_construct()


llm_service = LLMService()