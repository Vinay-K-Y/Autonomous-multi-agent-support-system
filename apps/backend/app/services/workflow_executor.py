import time

from ai_core.state.support_state import SupportState
from ai_core.graph import invoke_sync, invoke_async

class WorkflowExecutor:

    def execute(self, state: SupportState) -> SupportState:
        """Synchronous execution for backward compatibility"""
        start = time.perf_counter()

        result = invoke_sync(state)

        elapsed = (time.perf_counter() - start) * 1000

        result.metadata.processing_time_ms = elapsed

        return result

    async def execute_async(self, state: SupportState) -> SupportState:
        """Asynchronous execution for DB compatibility"""
        start = time.perf_counter()

        result = await invoke_async(state)

        elapsed = (time.perf_counter() - start) * 1000

        result.metadata.processing_time_ms = elapsed

        return result