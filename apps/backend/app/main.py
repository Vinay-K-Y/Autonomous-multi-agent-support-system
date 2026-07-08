from fastapi import FastAPI

from app.routers.support import router as support_router
from app.routers.health import router as health_router

app = FastAPI(
    title="Autonomous Multi-Agent Support System",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "Autonomous Multi-Agent Support System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "support": "/api/v1/support",
            "docs": "/docs"
        }
    }


app.include_router(health_router)
app.include_router(support_router)