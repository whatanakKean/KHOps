"""Pipeline Service"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import logging
from khops.db.models.pipeline import Pipeline
from khops.server.schemas.pipeline import PipelineCreate, PipelineUpdate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class PipelineService(BaseService[Pipeline, PipelineCreate, PipelineUpdate]):
    """Service for pipeline operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Pipeline)
    
    async def get_by_name(self, name: str) -> Optional[Pipeline]:
        """Get pipeline by name"""
        try:
            return self.db.query(Pipeline).filter(Pipeline.name == name).first()
        except Exception as e:
            logger.error(f"Error getting pipeline by name: {str(e)}")
            raise
    
    async def list_pipelines(self, skip: int = 0, limit: int = 10) -> tuple[List[Pipeline], int]:
        """List all pipelines with count"""
        try:
            pipelines = await self.get_all(skip=skip, limit=limit)
            total = await self.get_count()
            return pipelines, total
        except Exception as e:
            logger.error(f"Error listing pipelines: {str(e)}")
            raise
