"""Pipeline Service"""

import logging
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from khops.db.models.pipeline import Pipeline
from khops.server.schemas.pipeline import PipelineCreate, PipelineUpdate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class PipelineService(BaseService[Pipeline, PipelineCreate, PipelineUpdate]):
    """Service for pipeline operations"""

    def __init__(self, db: Session):
        super().__init__(db, Pipeline)

    async def get_by_name(self, name: str, project_id: Optional[int] = None) -> Optional[Pipeline]:
        """Get pipeline by name with optional project filtering."""
        try:
            query = self.db.query(Pipeline).filter(Pipeline.name == name)
            if project_id is not None:
                query = query.filter(Pipeline.project_id == project_id)
            return query.order_by(Pipeline.created_at.desc()).first()
        except Exception as e:
            logger.error(f"Error getting pipeline by name: {str(e)}")
            raise

    async def get_versions(
        self,
        name: str,
        project_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Pipeline]:
        """Get all versions of a pipeline."""
        try:
            query = self.db.query(Pipeline).filter(Pipeline.name == name)
            if project_id is not None:
                query = query.filter(Pipeline.project_id == project_id)
            return query.order_by(Pipeline.created_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting pipeline versions for {name}: {str(e)}")
            raise

    async def list_pipelines(
        self, skip: int = 0, limit: int = 10, project_id: Optional[int] = None
    ) -> tuple[List[Pipeline], int]:
        """List all pipelines with optional project filtering."""
        try:
            query = self.db.query(Pipeline)
            if project_id is not None:
                query = query.filter(Pipeline.project_id == project_id)
            pipelines = query.offset(skip).limit(limit).all()
            total = query.count()
            return pipelines, total
        except Exception as e:
            logger.error(f"Error listing pipelines: {str(e)}")
            raise
