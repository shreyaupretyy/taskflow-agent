"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Check if all services are ready
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
