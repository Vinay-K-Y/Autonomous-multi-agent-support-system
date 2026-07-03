from datetime import datetime

from pydantic import BaseModel, Field


class ProcessingMetadata(BaseModel):

    request_id: str

    started_at: datetime = Field(default_factory=datetime.utcnow)

    processing_time_ms: float = 0

    llm_provider: str = ""

    llm_model: str = ""

    workflow_version: str = "1.0"