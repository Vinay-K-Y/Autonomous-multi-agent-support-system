from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories import ConversationRepository, MessageRepository
from typing import List
from ai_core.memory.models import ConversationHistory


class ConversationManagerDB:
    """
    Database-backed conversation manager.
    Replaces the in-memory MemoryStore with PostgreSQL persistence.
    """

    def __init__(self):
        pass  # Database session will be passed to methods

    async def add_user_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        message: str,
    ):
        # Ensure conversation exists
        conversation = await ConversationRepository.get_by_id(db, conversation_id)
        if not conversation:
            # Create conversation if it doesn't exist
            conversation = await ConversationRepository.create(
                db,
                customer_id=conversation_id,  # Use conversation_id as customer_id for now
                conversation_id=conversation_id,
            )

        # Add user message
        await MessageRepository.create(
            db,
            conversation_id=conversation_id,
            role="user",
            content=message,
        )

    async def add_assistant_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        message: str,
    ):
        # Ensure conversation exists
        conversation = await ConversationRepository.get_by_id(db, conversation_id)
        if not conversation:
            conversation = await ConversationRepository.create(
                db,
                customer_id=conversation_id,
                conversation_id=conversation_id,
            )

        # Add assistant message
        await MessageRepository.create(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=message,
        )

    async def history(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> ConversationHistory:
        messages = await MessageRepository.get_by_conversation(db, conversation_id)
        # Convert DB Message objects to ConversationMessage objects
        from ai_core.memory.models import ConversationMessage
        conversation_messages = [
            ConversationMessage(role=m.role, content=m.content)
            for m in messages
        ]
        # Return ConversationHistory object to match MemoryStore interface
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=conversation_messages
        )

    async def formatted_history(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> str:
        history = await self.history(db, conversation_id)
        return "\n".join(
            f"{m.role.upper()}: {m.content}"
            for m in history.messages
        )

    async def clear(
        self,
        db: AsyncSession,
        conversation_id: str,
    ):
        # In a real implementation, you might want to soft delete or archive
        # For now, we'll just update the conversation status
        await ConversationRepository.update_status(db, conversation_id, "archived")


# Singleton instance for backward compatibility
conversation_manager_db = ConversationManagerDB()
