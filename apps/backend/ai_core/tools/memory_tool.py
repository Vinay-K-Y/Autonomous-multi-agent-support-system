from ai_core.memory.conversation_manager import conversation_manager
from ai_core.tools.base_tool import BaseTool


class MemoryTool(BaseTool):

    name = "memory"

    def execute(
        self,
        conversation_id: str,
    ):

        return conversation_manager.formatted_history(
            conversation_id
        )