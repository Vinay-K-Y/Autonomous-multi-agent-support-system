from ai_core.memory.models import (
    ConversationHistory,
    ConversationMessage,
)


class MemoryStore:
    """
    Temporary in-memory storage.

    Can later be replaced by Redis,
    PostgreSQL,
    MongoDB,
    etc.
    """

    def __init__(self):

        self._store: dict[
            str,
            ConversationHistory,
        ] = {}

    def get(
        self,
        conversation_id: str,
    ) -> ConversationHistory:

        if conversation_id not in self._store:

            self._store[conversation_id] = ConversationHistory(
                conversation_id=conversation_id
            )

        return self._store[conversation_id]

    def add_message(
        self,
        conversation_id: str,
        message: ConversationMessage,
    ) -> None:

        history = self.get(conversation_id)

        history.messages.append(message)

    def clear(
        self,
        conversation_id: str,
    ):

        self._store.pop(
            conversation_id,
            None,
        )