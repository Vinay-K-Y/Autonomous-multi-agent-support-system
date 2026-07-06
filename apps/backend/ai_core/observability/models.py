from datetime import datetime
from pydantic import BaseModel, Field


class AgentTrace(BaseModel):
    agent: str
    started_at: datetime
    finished_at: datetime | None = None

    duration_ms: float = 0

    status: str = "running"

    input_summary: str = ""
    output_summary: str = ""

    error: str | None = None


class WorkflowTrace(BaseModel):

    workflow_id: str

    traces: list[AgentTrace] = Field(default_factory=list)

    started_at: datetime

    finished_at: datetime | None = None

    total_duration_ms: float = 0