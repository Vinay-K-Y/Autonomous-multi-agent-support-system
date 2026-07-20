from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import os

# Only create engine if DATABASE_URL is set and not a placeholder
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if database_url and not database_url.startswith("postgresql+asyncpg://user:password"):
    try:
        engine = create_async_engine(
            database_url,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.DEBUG,
        )
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        Base = declarative_base()
        database_available = True
    except Exception:
        database_available = False
        engine = None
        AsyncSessionLocal = None
        Base = None
else:
    database_available = False
    engine = None
    AsyncSessionLocal = None
    Base = None


async def get_db() -> AsyncSession:
    if not database_available or AsyncSessionLocal is None:
        raise RuntimeError("Database not available. Please configure DATABASE_URL in .env")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
