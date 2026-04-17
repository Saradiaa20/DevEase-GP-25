"""Health and system status routes."""

from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevEase API", "version": "1.0.0"}
