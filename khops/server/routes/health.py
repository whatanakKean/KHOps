"""Route handlers for health checks"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed system health check"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"ready": True}
