from typing import Optional

from pydantic import BaseModel
from ai_core.models.knowledge import KnowledgeOutput
from ai_core.models.response import ResponseOutput
from ai_core.models.ticket import TicketOutput
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.human_review import HumanReview
from ai_core.models.metadata import ProcessingMetadata
from ai_core.models.intent import IntentOutput
from ai_core.models.workflow import WorkflowContext
from pydantic import Field
from ai_core.models.decision import DecisionResult
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.observability.models import WorkflowTrace

class SupportState(BaseModel):

    request: CustomerRequest

    metadata: ProcessingMetadata

    intent: Optional[IntentOutput] = None

    knowledge: Optional[KnowledgeOutput] = None
    response: Optional[ResponseOutput] = None
    ticket: Optional[TicketOutput] = None

    human_review: HumanReview = HumanReview()

    workflow: WorkflowContext = WorkflowContext()

    trace: WorkflowTrace | None = None

    conversation_history: str = ""

    execution_plan: ExecutionPlan | None = None
    decision: DecisionResult | None = None
    tool_results: dict = Field(default_factory=dict)

    # Benchmark/testing control flag: when True, forces the graph to take
    # the full planner -> decision -> tool_executor path even for requests
    # that would otherwise qualify for the conditional skip-to-response
    # shortcut (see ai_core/graph/builder.py::route_after_intent). Used by
    # scripts/benchmark_conditional_routing.py to run the same query
    # through both configurations for an apples-to-apples comparison.
    # Defaults to False, so normal request handling is unaffected.
    force_full_pipeline: bool = False