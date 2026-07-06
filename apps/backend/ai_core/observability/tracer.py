from datetime import datetime, timezone
from uuid import uuid4

from ai_core.observability.models import (
    AgentTrace,
    WorkflowTrace,
)


class WorkflowTracer:

    def __init__(self):

        self.workflow = WorkflowTrace(
            workflow_id=str(uuid4()),
            started_at=datetime.now(timezone.utc),
        )

    def start_agent(
        self,
        name: str,
        summary: str = "",
    ):

        trace = AgentTrace(
            agent=name,
            started_at=datetime.now(timezone.utc),
            input_summary=summary,
        )

        self.workflow.traces.append(trace)

    def finish_agent(
        self,
        output: str = "",
    ):

        trace = self.workflow.traces[-1]

        trace.finished_at = datetime.now(timezone.utc)

        trace.duration_ms = (
            trace.finished_at
            - trace.started_at
        ).total_seconds() * 1000

        trace.output_summary = output

        trace.status = "completed"

    def fail_agent(
        self,
        error: Exception,
    ):

        trace = self.workflow.traces[-1]

        trace.finished_at = datetime.now(timezone.utc)

        trace.status = "failed"

        trace.error = str(error)

    def finish_workflow(self):

        self.workflow.finished_at = datetime.now(timezone.utc)

        self.workflow.total_duration_ms = (
            self.workflow.finished_at
            - self.workflow.started_at
        ).total_seconds() * 1000