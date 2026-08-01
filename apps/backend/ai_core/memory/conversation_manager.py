from ai_core.memory.memory_store import MemoryStore
from ai_core.memory.models import ConversationMessage
from ai_core.memory.conversation_manager_db import conversation_manager_db
from sqlalchemy.ext.asyncio import AsyncSession


class ConversationManager:
    """
    High-level interface for managing conversations.
    Supports both in-memory (for development) and database (for production) storage.
    """

    def __init__(self, use_db: bool = False, db_session: AsyncSession = None):
        self.use_db = use_db
        self.db_session = db_session
        self.store = MemoryStore() if not use_db else None

    def add_user_message(
        self,
        conversation_id: str,
        message: str,
        db_session: AsyncSession = None,
    ):
        session = db_session if db_session is not None else self.db_session
        if self.use_db and session:
            return conversation_manager_db.add_user_message(
                session,
                conversation_id,
                message,
            )
        else:
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
        db_session: AsyncSession = None,
    ):
        session = db_session if db_session is not None else self.db_session
        if self.use_db and session:
            return conversation_manager_db.add_assistant_message(
                session,
                conversation_id,
                message,
            )
        else:
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
        db_session: AsyncSession = None,
    ):
        session = db_session if db_session is not None else self.db_session
        if self.use_db and session:
            return conversation_manager_db.history(
                session,
                conversation_id,
            )
        else:
            return self.store.get(
                conversation_id
            )

    def formatted_history(
        self,
        conversation_id: str,
        db_session: AsyncSession = None,
    ) -> str:
        session = db_session if db_session is not None else self.db_session
        if self.use_db and session:
            return conversation_manager_db.formatted_history(
                session,
                conversation_id,
            )
        else:
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
        if self.use_db and self.db_session:
            return conversation_manager_db.clear(
                self.db_session,
                conversation_id,
            )
        else:
            self.store.clear(
                conversation_id
            )


# Default instance using in-memory storage for backward compatibility
conversation_manager = ConversationManager(use_db=False)