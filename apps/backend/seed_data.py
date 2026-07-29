"""
Synthetic data seeding script for testing the support system.
This script creates test users, conversations, messages, tickets, and knowledge base entries.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid

# Add the app directory to the path
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.models import (
    User, Conversation, Message, Ticket, 
    SupportRequestLog, HumanReview
)
from app.core.config import settings

# Password hashing - use a simpler method for seed data to avoid bcrypt issues
import hashlib
def hash_password(password: str) -> str:
    """Simple password hashing for seed data"""
    # Use SHA-256 for seed data (not production secure, but fine for testing)
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment variables")
    sys.exit(1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_test_users():
    """Create test users with different roles"""
    users_data = [
        {
            "email": "admin@example.com",
            "full_name": "System Administrator",
            "is_active": True,
            "is_superuser": True,
            "password": "admin123"
        },
        {
            "email": "support.agent@example.com",
            "full_name": "Support Agent",
            "is_active": True,
            "is_superuser": False,
            "password": "support123"
        },
        {
            "email": "customer1@example.com",
            "full_name": "John Customer",
            "is_active": True,
            "is_superuser": False,
            "password": "customer123"
        },
        {
            "email": "customer2@example.com",
            "full_name": "Jane Customer",
            "is_active": True,
            "is_superuser": False,
            "password": "customer123"
        },
        {
            "email": "customer3@example.com",
            "full_name": "Bob Customer",
            "is_active": True,
            "is_superuser": False,
            "password": "customer123"
        }
    ]
    
    async with AsyncSessionLocal() as session:
        users = []
        for user_data in users_data:
            # Check if user already exists
            from sqlalchemy import select
            existing = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            if existing.scalar_one_or_none():
                print(f"User {user_data['email']} already exists, skipping...")
                continue
            
            user = User(
                id=str(uuid.uuid4()),
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                is_active=user_data["is_active"],
                is_superuser=user_data["is_superuser"]
            )
            session.add(user)
            users.append(user)
        
        await session.commit()
        print(f"Created {len(users)} test users")
        return users


async def create_test_conversations_and_messages(users):
    """Create test conversations with messages"""
    conversations_data = [
        {
            "customer_id": users[2].id,  # customer1
            "messages": [
                {"role": "user", "content": "I need help with my recent order"},
                {"role": "assistant", "content": "I'd be happy to help you with your order. Could you please provide your order number?"},
                {"role": "user", "content": "My order number is #12345"},
            ]
        },
        {
            "customer_id": users[2].id,  # customer1
            "messages": [
                {"role": "user", "content": "What's your refund policy?"},
                {"role": "assistant", "content": "Our refund policy allows returns within 30 days of purchase. Would you like me to help you process a refund?"},
            ]
        },
        {
            "customer_id": users[3].id,  # customer2
            "messages": [
                {"role": "user", "content": "My account seems to be locked"},
                {"role": "assistant", "content": "I'm sorry to hear that. Let me check your account status. Can you provide your email address?"},
                {"role": "user", "content": "customer2@example.com"},
                {"role": "assistant", "content": "Thank you. I can see your account is locked due to multiple failed login attempts. I can help you unlock it."},
            ]
        },
        {
            "customer_id": users[4].id,  # customer3
            "messages": [
                {"role": "user", "content": "I received the wrong product"},
                {"role": "assistant", "content": "I apologize for the mix-up. Let me help you get this resolved. What product did you order vs what did you receive?"},
            ]
        }
    ]
    
    async with AsyncSessionLocal() as session:
        conversations = []
        base_time = datetime.utcnow() - timedelta(days=7)
        
        for conv_data in conversations_data:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                customer_id=conv_data["customer_id"],
                status="active",
                created_at=base_time
            )
            session.add(conversation)
            await session.flush()
            
            message_time = base_time + timedelta(minutes=5)
            for msg_data in conv_data["messages"]:
                message = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation.id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    created_at=message_time
                )
                session.add(message)
                message_time += timedelta(minutes=2)
            
            conversations.append(conversation)
            base_time += timedelta(hours=1)
        
        await session.commit()
        print(f"Created {len(conversations)} test conversations with messages")
        return conversations


async def create_test_tickets(users, conversations):
    """Create test support tickets"""
    tickets_data = [
        {
            "conversation_id": conversations[0].id,
            "ticket_id": "TICK-12345",
            "summary": "Order #12345 - Missing Item",
            "description": "Customer reports missing item from order #12345",
            "priority": "high",
            "status": "open",
            "assigned_team": "fulfillment"
        },
        {
            "conversation_id": conversations[2].id,
            "ticket_id": "TICK-12346",
            "summary": "Account Locked - Failed Login Attempts",
            "description": "Customer account locked due to multiple failed login attempts",
            "priority": "medium",
            "status": "in_progress",
            "assigned_team": "security"
        },
        {
            "conversation_id": conversations[3].id,
            "ticket_id": "TICK-12347",
            "summary": "Wrong Product Received",
            "description": "Customer received wrong product - needs exchange",
            "priority": "high",
            "status": "open",
            "assigned_team": None
        }
    ]
    
    async with AsyncSessionLocal() as session:
        tickets = []
        base_time = datetime.utcnow() - timedelta(days=5)
        
        for ticket_data in tickets_data:
            ticket = Ticket(
                id=str(uuid.uuid4()),
                conversation_id=ticket_data["conversation_id"],
                ticket_id=ticket_data["ticket_id"],
                summary=ticket_data["summary"],
                description=ticket_data["description"],
                priority=ticket_data["priority"],
                status=ticket_data["status"],
                assigned_team=ticket_data["assigned_team"],
                created_at=base_time
            )
            session.add(ticket)
            tickets.append(ticket)
            base_time += timedelta(hours=2)
        
        await session.commit()
        print(f"Created {len(tickets)} test tickets")
        return tickets


async def create_test_support_logs(users):
    """Create test support request logs"""
    logs_data = [
        {
            "conversation_id": str(uuid.uuid4()),
            "request_id": str(uuid.uuid4()),
            "intent": "subscription",
            "confidence": 0.85,
            "ticket_created": False,
            "requires_human_review": False,
            "processing_time_ms": 1250.0
        },
        {
            "conversation_id": str(uuid.uuid4()),
            "request_id": str(uuid.uuid4()),
            "intent": "account_management",
            "confidence": 0.92,
            "ticket_created": False,
            "requires_human_review": False,
            "processing_time_ms": 890.0
        },
        {
            "conversation_id": str(uuid.uuid4()),
            "request_id": str(uuid.uuid4()),
            "intent": "refund",
            "confidence": 0.78,
            "ticket_created": True,
            "requires_human_review": False,
            "processing_time_ms": 2100.0
        }
    ]
    
    async with AsyncSessionLocal() as session:
        logs = []
        base_time = datetime.utcnow() - timedelta(days=3)
        
        for log_data in logs_data:
            log = SupportRequestLog(
                id=str(uuid.uuid4()),
                conversation_id=log_data["conversation_id"],
                request_id=log_data["request_id"],
                intent=log_data["intent"],
                confidence=log_data["confidence"],
                ticket_created=log_data["ticket_created"],
                requires_human_review=log_data["requires_human_review"],
                processing_time_ms=log_data["processing_time_ms"],
                created_at=base_time
            )
            session.add(log)
            logs.append(log)
            base_time += timedelta(hours=4)
        
        await session.commit()
        print(f"Created {len(logs)} test support request logs")
        return logs


async def create_test_human_reviews(conversations):
    """Create test human reviews"""
    reviews_data = [
        {
            "conversation_id": conversations[0].id,
            "reason": "Customer requested escalation",
            "status": "approved",
            "reviewer_id": str(uuid.uuid4()),
            "review_notes": "Issue resolved successfully, customer satisfied"
        },
        {
            "conversation_id": conversations[2].id,
            "reason": "Complex account security issue",
            "status": "approved",
            "reviewer_id": str(uuid.uuid4()),
            "review_notes": "Account security verified and restored"
        }
    ]
    
    async with AsyncSessionLocal() as session:
        reviews = []
        base_time = datetime.utcnow() - timedelta(days=2)
        
        for review_data in reviews_data:
            review = HumanReview(
                id=str(uuid.uuid4()),
                conversation_id=review_data["conversation_id"],
                reason=review_data["reason"],
                status=review_data["status"],
                reviewer_id=review_data["reviewer_id"],
                review_notes=review_data["review_notes"],
                created_at=base_time,
                reviewed_at=base_time + timedelta(hours=1)
            )
            session.add(review)
            reviews.append(review)
            base_time += timedelta(hours=6)
        
        await session.commit()
        print(f"Created {len(reviews)} test human reviews")
        return reviews


async def main():
    """Main seeding function"""
    print("Starting synthetic data seeding...")
    print("=" * 60)
    
    try:
        # Create test users
        print("\n1. Creating test users...")
        users = await create_test_users()
        
        # Create conversations and messages
        print("\n2. Creating test conversations and messages...")
        conversations = await create_test_conversations_and_messages(users)
        
        # Create tickets
        print("\n3. Creating test tickets...")
        tickets = await create_test_tickets(users, conversations)
        
        # Create support logs
        print("\n4. Creating test support request logs...")
        logs = await create_test_support_logs(users)
        
        # Create human reviews
        print("\n5. Creating test human reviews...")
        reviews = await create_test_human_reviews(conversations)
        
        print("\n" + "=" * 60)
        print("✅ Synthetic data seeding completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Conversations: {len(conversations)}")
        print(f"  - Tickets: {len(tickets)}")
        print(f"  - Support Logs: {len(logs)}")
        print(f"  - Human Reviews: {len(reviews)}")
        print("\nTest Credentials:")
        print("  - Admin: admin@example.com / admin123")
        print("  - Support Agent: support.agent@example.com / support123")
        print("  - Customer 1: customer1@example.com / customer123")
        print("  - Customer 2: customer2@example.com / customer123")
        print("  - Customer 3: customer3@example.com / customer123")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
