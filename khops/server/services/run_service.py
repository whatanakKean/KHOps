"""Run Service"""

from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from khops.db.models.run import Run
from khops.server.schemas.run import RunCreate, RunUpdate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class RunService(BaseService[Run, RunCreate, RunUpdate]):
    """Service for run operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Run)
    
    async def get_by_pipeline(self, pipeline_id: int, skip: int = 0, limit: int = 10) -> List[Run]:
        """Get runs for a specific pipeline"""
        try:
            return await self.get_all(skip=skip, limit=limit, filters={"pipeline_id": pipeline_id})
        except Exception as e:
            logger.error(f"Error getting runs for pipeline: {str(e)}")
            raise
    
    async def list_runs(self, skip: int = 0, limit: int = 10) -> tuple[List[Run], int]:
        """List all runs with count"""
        try:
            runs = await self.get_all(skip=skip, limit=limit)
            total = await self.get_count()
            return runs, total
        except Exception as e:
            logger.error(f"Error listing runs: {str(e)}")
            raise
