"""Route handlers for metrics"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from khops.server.dependencies import get_db
from khops.server.schemas.metrics import MetricsCreate, MetricsResponse, MetricsListResponse
from khops.server.services.metrics_service import MetricsService

router = APIRouter()


@router.get("/metrics", response_model=MetricsListResponse)
async def get_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all metrics with pagination"""
    try:
        service = MetricsService(db)
        metrics, total = await service.list_metrics(skip=skip, limit=limit)
        return MetricsListResponse(
            metrics=metrics,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{metric_name}", response_model=List[MetricsResponse])
async def get_metric(
    metric_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get specific metric history"""
    try:
        service = MetricsService(db)
        metrics = await service.get_all(skip=skip, limit=limit, filters={"name": metric_name})
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/log", response_model=MetricsResponse)
async def log_metric(
    metric_in: MetricsCreate,
    db: Session = Depends(get_db),
):
    """Log a new metric"""
    try:
        service = MetricsService(db)
        metric = await service.create(metric_in)
        return metric
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error logging metric: {str(e)}")
