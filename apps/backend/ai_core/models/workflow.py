from typing import Optional

from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    current_agent: Optional[str] = None

    completed_agents: list[str] = Field(default_factory=list)

    next_agent: Optional[str] = None

    retry_count: int = 0

    status: str = "running"