from typing import Dict

from pydantic import BaseModel


class WorkflowTrace(BaseModel):

    workflow_id: str

    routing_reasons: list[str]

    agent_timings: Dict[str, float]

    llm_calls: int

    llm_fallback_count: int

    retrieved_documents: int