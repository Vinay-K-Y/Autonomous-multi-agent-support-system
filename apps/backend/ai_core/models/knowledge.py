from typing import List

from pydantic import BaseModel, Field


class KnowledgeSource(BaseModel):
    title: str
    source: str
    confidence: float


class KnowledgeOutput(BaseModel):
    answer: str = ""

    sources: List[KnowledgeSource] = Field(default_factory=list)

    confidence: float = 0.0