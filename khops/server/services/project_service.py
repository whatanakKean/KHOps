"""Service layer for project operations."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from khops.db.models.project import Project
from khops.server.schemas.project import ProjectCreate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ProjectService(BaseService[Project, ProjectCreate, ProjectCreate]):
    """Service for project CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(db, Project)

    async def get_by_name(self, name: str) -> Optional[Project]:
        try:
            return self.db.query(Project).filter(Project.name == name).first()
        except Exception as e:
            logger.error(f"Error getting project by name: {str(e)}")
            raise

    async def list_projects(self, skip: int = 0, limit: int = 10) -> tuple[List[Project], int]:
        try:
            projects = await self.get_all(skip=skip, limit=limit)
            total = await self.get_count()
            return projects, total
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            raise
