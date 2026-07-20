from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base, database_available

# Only define models if database is available
if database_available and Base is not None:

    class User(Base):
        __tablename__ = "users"

        id = Column(String, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        hashed_password = Column(String, nullable=False)
        full_name = Column(String)
        is_active = Column(Boolean, default=True)
        is_superuser = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        conversations = relationship("Conversation", back_populates="user")


    class Conversation(Base):
        __tablename__ = "conversations"

        id = Column(String, primary_key=True, index=True)
        user_id = Column(String, ForeignKey("users.id"), nullable=True)
        customer_id = Column(String, index=True)
        language = Column(String, default="en")
        channel = Column(String, default="web")
        status = Column(String, default="active")
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        user = relationship("User", back_populates="conversations")
        messages = relationship("Message", back_populates="conversation")
        tickets = relationship("Ticket", back_populates="conversation")


    class Message(Base):
        __tablename__ = "messages"

        id = Column(String, primary_key=True, index=True)
        conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
        role = Column(String, nullable=False)  # "user" or "assistant"
        content = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        conversation = relationship("Conversation", back_populates="messages")


    class Ticket(Base):
        __tablename__ = "tickets"

        id = Column(String, primary_key=True, index=True)
        conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
        ticket_id = Column(String, unique=True, index=True)  # External system ticket ID
        priority = Column(String, default="medium")
        status = Column(String, default="open")
        assigned_team = Column(String)
        summary = Column(Text)
        description = Column(Text)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        conversation = relationship("Conversation", back_populates="tickets")


    class SupportRequestLog(Base):
        __tablename__ = "support_request_logs"

        id = Column(String, primary_key=True, index=True)
        conversation_id = Column(String, index=True)
        request_id = Column(String, index=True)
        intent = Column(String)
        confidence = Column(Float)
        ticket_created = Column(Boolean, default=False)
        requires_human_review = Column(Boolean, default=False)
        processing_time_ms = Column(Float)
        error_message = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)


    class HumanReview(Base):
        __tablename__ = "human_reviews"

        id = Column(String, primary_key=True, index=True)
        conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
        reason = Column(Text)
        status = Column(String, default="pending")  # pending, approved, rejected
        reviewer_id = Column(String, nullable=True)
        review_notes = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        reviewed_at = Column(DateTime, nullable=True)

        conversation = relationship("Conversation")
else:
    # Create stub classes when database is not available
    # These will raise errors if used, preventing accidental database operations
    class User:
        pass
    class Conversation:
        pass
    class Message:
        pass
    class Ticket:
        pass
    class SupportRequestLog:
        pass
    class HumanReview:
        pass
