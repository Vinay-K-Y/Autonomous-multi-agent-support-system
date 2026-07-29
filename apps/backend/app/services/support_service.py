from app.mappers import SupportMapper
from app.services.workflow_executor import WorkflowExecutor
from ai_core.factories import SupportStateFactory
from ai_core.memory.conversation_manager import ConversationManager
from app.db import AsyncSessionLocal, database_available


class SupportService:

    def __init__(self):
        self.executor = WorkflowExecutor()
        # Use database-backed conversation manager if database is available
        self.use_db_memory = database_available
        self.conversation_manager = None

    def _get_conversation_manager(self):
        """Get conversation manager instance"""
        if self.conversation_manager is None:
            if self.use_db_memory:
                # Database-backed storage
                from app.db import get_db
                self.conversation_manager = ConversationManager(use_db=True, db_session=None)
            else:
                # In-memory storage
                self.conversation_manager = ConversationManager(use_db=False)
        return self.conversation_manager

    def process_request(
        self,
        message: str,
        customer_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
        channel: str = "web",
    ):
        # Get conversation manager
        conv_manager = self._get_conversation_manager()

        # If using database, we need a session
        db_session = None
        if self.use_db_memory:
            import asyncio
            # For sync execution, we'll use in-memory for now
            # In production, this should be async
            conv_manager = ConversationManager(use_db=False)
            print("Warning: Database-backed memory not available in sync mode, using in-memory")

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