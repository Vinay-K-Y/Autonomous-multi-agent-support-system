import time

from ai_core.state.support_state import SupportState
from ai_core.graph import invoke_sync

class WorkflowExecutor:

    def execute(self, state: SupportState) -> SupportState:

        start = time.perf_counter()

        result = invoke_sync(state)

        elapsed = (time.perf_counter() - start) * 1000

        result.metadata.processing_time_ms = elapsed

        return result