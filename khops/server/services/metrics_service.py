"""Metrics Service"""

from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from khops.db.models.metrics import Metrics
from khops.server.schemas.metrics import MetricsCreate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class MetricsService(BaseService[Metrics, MetricsCreate, MetricsCreate]):
    """Service for metrics operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Metrics)
    
    async def get_by_run(self, run_id: int, skip: int = 0, limit: int = 10) -> List[Metrics]:
        """Get metrics for a specific run"""
        try:
            return await self.get_all(skip=skip, limit=limit, filters={"run_id": run_id})
        except Exception as e:
            logger.error(f"Error getting metrics for run: {str(e)}")
            raise
    
    async def list_metrics(self, skip: int = 0, limit: int = 10) -> tuple[List[Metrics], int]:
        """List all metrics with count"""
        try:
            metrics = await self.get_all(skip=skip, limit=limit)
            total = await self.get_count()
            return metrics, total
        except Exception as e:
            logger.error(f"Error listing metrics: {str(e)}")
            raise
