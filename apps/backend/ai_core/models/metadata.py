from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ProcessingMetadata(BaseModel):

    request_id: str

    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    processing_time_ms: float = 0

    llm_provider: str = ""

    llm_model: str = ""

    workflow_version: str = "1.0"

    routing_reasons: list[str] = Field(default_factory=list)

    agent_timings: dict[str, float] = Field(default_factory=dict)

    retrieved_documents: int = 0

    llm_call_count: int = 0

    llm_fallback_count: int = 0

    execution_trace: dict[str, Any] = Field(default_factory=dict)

    planner_reasoning: str = ""

    decision_reasoning: str = ""

    blocked_tools: list[str] = Field(default_factory=list)