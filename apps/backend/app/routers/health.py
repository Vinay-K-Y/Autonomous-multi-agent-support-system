from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "Autonomous Multi-Agent Support System",
        "version": "1.0.0",
    }