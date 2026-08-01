from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Conversation, Message, Ticket, SupportRequestLog, HumanReview
from datetime import datetime
import uuid


class UserRepository:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, email: str, hashed_password: str, full_name: str = None) -> User:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


class ConversationRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_customer_id(db: AsyncSession, customer_id: str) -> List[Conversation]:
        result = await db.execute(
            select(Conversation).where(Conversation.customer_id == customer_id)
        )
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        customer_id: str,
        user_id: str = None,
        language: str = "en",
        channel: str = "web",
        conversation_id: str = None,
    ) -> Conversation:
        # Use provided conversation_id if available, otherwise generate new UUID
        conv_id = conversation_id if conversation_id else str(uuid.uuid4())
        
        conversation = Conversation(
            id=conv_id,
            user_id=user_id,
            customer_id=customer_id,
            language=language,
            channel=channel,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def update_status(db: AsyncSession, conversation_id: str, status: str) -> Conversation:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.status = status
            conversation.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(conversation)
        return conversation


class MessageRepository:
    @staticmethod
    async def get_by_conversation(db: AsyncSession, conversation_id: str) -> List[Message]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
    ) -> Message:
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message


class TicketRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, ticket_id: str) -> Optional[Ticket]:
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_external_id(db: AsyncSession, external_ticket_id: str) -> Optional[Ticket]:
        result = await db.execute(select(Ticket).where(Ticket.ticket_id == external_ticket_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: str,
        external_ticket_id: str,
        priority: str = "medium",
        assigned_team: str = None,
        summary: str = None,
        description: str = None,
    ) -> Ticket:
        ticket = Ticket(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            ticket_id=external_ticket_id,
            priority=priority,
            assigned_team=assigned_team,
            summary=summary,
            description=description,
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket


class SupportRequestLogRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: str,
        request_id: str,
        intent: str = None,
        confidence: float = None,
        ticket_created: bool = False,
        requires_human_review: bool = False,
        processing_time_ms: float = None,
        error_message: str = None,
    ) -> SupportRequestLog:
        log = SupportRequestLog(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            request_id=request_id,
            intent=intent,
            confidence=confidence,
            ticket_created=ticket_created,
            requires_human_review=requires_human_review,
            processing_time_ms=processing_time_ms,
            error_message=error_message,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log


class HumanReviewRepository:
    @staticmethod
    async def get_by_conversation(db: AsyncSession, conversation_id: str) -> Optional[HumanReview]:
        result = await db.execute(
            select(HumanReview).where(HumanReview.conversation_id == conversation_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        conversation_id: str,
        reason: str,
    ) -> HumanReview:
        review = HumanReview(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            reason=reason,
            status="pending",
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def update_status(
        db: AsyncSession,
        review_id: str,
        status: str,
        reviewer_id: str = None,
        review_notes: str = None,
    ) -> HumanReview:
        result = await db.execute(select(HumanReview).where(HumanReview.id == review_id))
        review = result.scalar_one_or_none()
        if review:
            review.status = status
            review.reviewer_id = reviewer_id
            review.review_notes = review_notes
            review.reviewed_at = datetime.utcnow()
            await db.commit()
            await db.refresh(review)
        return review
