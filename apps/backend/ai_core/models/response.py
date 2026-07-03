from typing import List

from pydantic import BaseModel, Field


class ResponseOutput(BaseModel):
    response: str = ""

    tone: str = "professional"

    follow_up_actions: List[str] = Field(default_factory=list)

    confidence: float = 0.0