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

class SupportState(BaseModel):

    request: CustomerRequest

    metadata: ProcessingMetadata

    intent: Optional[IntentOutput] = None

    knowledge: Optional[KnowledgeOutput] = None
    response: Optional[ResponseOutput] = None
    ticket: Optional[TicketOutput] = None

    human_review: HumanReview = HumanReview()

    workflow: WorkflowContext = WorkflowContext()

    conversation_history: str = ""

    execution_plan: ExecutionPlan | None = None
    decision: DecisionResult | None = None
    tool_results: dict = Field(default_factory=dict)