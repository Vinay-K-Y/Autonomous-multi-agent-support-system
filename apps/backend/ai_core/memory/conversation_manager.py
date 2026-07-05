from ai_core.memory.memory_store import MemoryStore
from ai_core.memory.models import ConversationMessage


class ConversationManager:
    """
    High-level interface for managing conversations.
    """

    def __init__(self):

        self.store = MemoryStore()

    def add_user_message(
        self,
        conversation_id: str,
        message: str,
    ):

        self.store.add_message(
            conversation_id,
            ConversationMessage(
                role="user",
                content=message,
            ),
        )

    def add_assistant_message(
        self,
        conversation_id: str,
        message: str,
    ):

        self.store.add_message(
            conversation_id,
            ConversationMessage(
                role="assistant",
                content=message,
            ),
        )

    def history(
        self,
        conversation_id: str,
    ):

        return self.store.get(
            conversation_id
        )

    def formatted_history(
        self,
        conversation_id: str,
    ) -> str:

        history = self.history(
            conversation_id
        )

        return "\n".join(
            f"{m.role.upper()}: {m.content}"
            for m in history.messages
        )

    def clear(
        self,
        conversation_id: str,
    ):

        self.store.clear(
            conversation_id
        )


conversation_manager = ConversationManager()