import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import AsyncSessionLocal, engine
from app.db.models import User, Conversation, Message, Ticket, SupportRequestLog, HumanReview
from sqlalchemy import delete

async def clear_all_data():
    async with AsyncSessionLocal() as session:
        # Delete in order of dependencies
        await session.execute(delete(HumanReview))
        await session.execute(delete(SupportRequestLog))
        await session.execute(delete(Message))
        await session.execute(delete(Ticket))
        await session.execute(delete(Conversation))
        await session.execute(delete(User))
        await session.commit()
        print('Cleared all data from database')

asyncio.run(clear_all_data())
