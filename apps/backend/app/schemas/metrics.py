from pydantic import BaseModel


class MetricsResponse(BaseModel):

    workflows: int

    llm_calls: int

    average_latency_ms: float

    knowledge_queries: int

    tickets_created: int