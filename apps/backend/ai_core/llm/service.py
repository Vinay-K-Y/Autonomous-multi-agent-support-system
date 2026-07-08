from typing import Type
import logging

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from ai_core.llm.factory import LLMFactory
from ai_core.models.intent import IntentOutput
from ai_core.models.response import ResponseOutput

logger = logging.getLogger(__name__)


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
        except Exception as e:
            logger.error(f"LLM generation failed: {type(e).__name__}: {e}", exc_info=True)
            if output_schema is IntentOutput:
                return IntentOutput(
                    intent="refund",
                    confidence=0.2,
                    reasoning=f"Fallback intent detection due to LLM error: {type(e).__name__}",
                )
            if output_schema is ResponseOutput:
                return ResponseOutput(
                    response="I apologize, but I encountered an error generating a response. Please try again.",
                    tone="professional",
                    confidence=0.0,
                    follow_up_actions=[],
                )
            return output_schema.model_construct()


llm_service = LLMService()