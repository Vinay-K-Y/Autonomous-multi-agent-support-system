from ai_core.memory.conversation_manager import conversation_manager


class ConversationService:

    def get_history(
        self,
        conversation_id: str,
    ) -> str:

        return conversation_manager.get_history(
            conversation_id
        )

    def clear(
        self,
        conversation_id: str,
    ):

        conversation_manager.clear(
            conversation_id
        )