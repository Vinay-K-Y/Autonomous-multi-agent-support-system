from ai_core.memory.conversation_manager import conversation_manager
from ai_core.tools.base_tool import BaseTool


class MemoryTool(BaseTool):

    name = "memory"
    description = "Retrieves previous conversation history."
    
    def execute(
        self,
        conversation_id: str,
    ):

        # Use the same singleton conversation_manager that SupportService uses
        # This ensures single source of truth for conversation memory
        return conversation_manager.formatted_history(
            conversation_id
        )