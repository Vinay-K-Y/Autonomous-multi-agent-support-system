from fastapi import FastAPI, Request
from app.middleware.request_logger import log_requests
from app.routers.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging
import logging
from app.routers.chat import router as chat_router


setup_logging()
logger = logging.getLogger(__name__)



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
app.include_router(health_router)
app.middleware("http")(log_requests)
app.include_router(chat_router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")

    return {
        "provider": settings.LLM_PROVIDER,
        "model": settings.MODEL_NAME,
    }