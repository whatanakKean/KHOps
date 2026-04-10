"""Model Service"""

from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from khops.db.models.model import Model
from khops.server.schemas.model import ModelCreate, ModelUpdate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ModelService(BaseService[Model, ModelCreate, ModelUpdate]):
    """Service for model registry operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Model)
    
    async def get_by_name(self, name: str) -> Optional[Model]:
        """Get latest model by name"""
        try:
            return self.db.query(Model).filter(Model.name == name).order_by(Model.created_at.desc()).first()
        except Exception as e:
            logger.error(f"Error getting model by name: {str(e)}")
            raise
    
    async def get_versions(self, name: str, skip: int = 0, limit: int = 10) -> List[Model]:
        """Get all versions of a model"""
        try:
            return self.db.query(Model).filter(Model.name == name).order_by(Model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting model versions: {str(e)}")
            raise
    
    async def promote(self, name: str, version: str, stage: str) -> Optional[Model]:
        """Promote a model to a new stage"""
        try:
            model = self.db.query(Model).filter(
                Model.name == name,
                Model.version == version
            ).first()
            
            if not model:
                return None
            
            model.stage = stage
            self.db.commit()
            self.db.refresh(model)
            logger.info(f"Promoted model {name}/{version} to {stage}")
            return model
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error promoting model: {str(e)}")
            raise
    
    async def list_models(self, skip: int = 0, limit: int = 10) -> tuple[List[Model], int]:
        """List all models with count"""
        try:
            models = await self.get_all(skip=skip, limit=limit)
            total = await self.get_count()
            return models, total
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise
