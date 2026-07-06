from pydantic import BaseModel


class WorkflowSummary(BaseModel):

    workflow_id: str

    status: str

    execution_time_ms: float

    planner_used: bool

    tool_count: int

    llm_calls: int