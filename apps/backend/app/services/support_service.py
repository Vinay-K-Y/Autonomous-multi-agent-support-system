from app.mappers import SupportMapper
from app.services.workflow_executor import WorkflowExecutor
from ai_core.factories import SupportStateFactory
from ai_core.memory.conversation_manager import conversation_manager
from app.db import AsyncSessionLocal, database_available


class SupportService:

    def __init__(self):
        self.executor = WorkflowExecutor()
        # Use the same singleton conversation_manager that MemoryTool uses
        # This ensures single source of truth for conversation memory
        self.conversation_manager = conversation_manager

    def process_request(
        self,
        message: str,
        customer_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
        channel: str = "web",
    ):
        # Use the singleton conversation_manager for consistency with MemoryTool
        conv_manager = self.conversation_manager

        # 1. Save user message to conversation history
        if conversation_id:
            conv_manager.add_user_message(conversation_id, message)

        # 2. Load conversation history if available
        conversation_history = None
        if conversation_id:
            history = conv_manager.history(conversation_id)
            if history and history.messages:
                conversation_history = conv_manager.formatted_history(conversation_id)
                print(f"Loaded conversation history for {conversation_id}: {len(history.messages)} messages")

        # 3. Initialize state using the factory with conversation history
        initial_state = SupportStateFactory.create(
            message=message,
            customer_id=customer_id,
            conversation_id=conversation_id,
            language=language,
            channel=channel,
            conversation_history=conversation_history,
        )

        # 4. Execute the workflow
        state = self.executor.execute(initial_state)

        # 5. Save assistant response to conversation history
        if conversation_id and state.response:
            conv_manager.add_assistant_message(conversation_id, state.response.response)

        # 6. Map the final state directly to the response object
        return SupportMapper.to_response(state)