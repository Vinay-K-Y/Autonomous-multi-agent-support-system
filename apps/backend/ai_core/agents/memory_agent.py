from ai_core.state.support_state import SupportState
from ai_core.tools.executor import tool_executor
import ai_core.tools


class MemoryAgent:
    """
    Loads conversation history into the workflow state.
    """

    async def run(
        self,
        state: SupportState,
    ) -> SupportState:

        conversation_id = state.request.conversation_id

        state.conversation_history = tool_executor.execute(
            "memory",
            conversation_id=conversation_id,
        )

        return state