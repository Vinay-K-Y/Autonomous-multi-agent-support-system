from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers.support import router as support_router
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.exceptions import setup_exception_handlers
from app.db import engine, Base, database_available
from app.core.config import settings
from app.core.logging_config import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables if database is configured
    app_logger.info("Starting application...")
    if database_available and engine and Base:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            app_logger.info("Database tables created successfully")
        except Exception as e:
            app_logger.error(f"Database connection failed: {e}")
            app_logger.warning("Application will run without database persistence")
    else:
        app_logger.warning("Database not configured. Application will run without database persistence.")
        app_logger.info("To enable database features, set DATABASE_URL in .env")
    yield
    # Shutdown: Close database connections
    app_logger.info("Shutting down application...")
    if database_available and engine:
        try:
            await engine.dispose()
            app_logger.info("Database connections closed")
        except Exception as e:
            app_logger.error(f"Error closing database connections: {e}")


app = FastAPI(
    title="Autonomous Multi-Agent Support System",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup rate limiting
setup_rate_limiting(app)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Setup exception handlers
setup_exception_handlers(app)


@app.get("/")
async def root():
    return {
        "message": "Autonomous Multi-Agent Support System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "support": "/api/v1/support",
            "auth": "/api/v1/auth",
            "docs": "/docs"
        },
        "features": {
            "authentication": "JWT-based authentication",
            "rate_limiting": "API rate limiting enabled",
            "database": "PostgreSQL persistence",
            "error_handling": "Agent fallback mechanisms"
        }
    }


# Include routers
app.include_router(health_router)
app.include_router(support_router)
app.include_router(auth_router)