from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate_structured(
        self,
        prompt: ChatPromptTemplate,
        output_schema: Type[BaseModel],
        variables: dict,
    ) -> BaseModel:
        """
        Generate validated structured output from an LLM.
        """
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate plain-text output from an LLM.
        """
        pass