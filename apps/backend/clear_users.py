import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import AsyncSessionLocal, engine
from app.db.models import User
from sqlalchemy import delete

async def clear_users():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(User))
        await session.commit()
        print('Deleted all users')

asyncio.run(clear_users())
