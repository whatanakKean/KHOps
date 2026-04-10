"""Model Service"""

from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from khops.db.models.model import Model
from khops.server.schemas.model import ModelCreate, ModelUpdate
from khops.server.schemas.model_promotion import ModelPromotionCreate
from khops.server.services.base_service import BaseService
from khops.server.services.model_promotion_service import ModelPromotionService

logger = logging.getLogger(__name__)


class ModelService(BaseService[Model, ModelCreate, ModelUpdate]):
    """Service for model registry operations"""

    def __init__(self, db: Session):
        super().__init__(db, Model)

    async def create(self, obj_in: ModelCreate) -> Model:
        """Create a new model with metadata field mapping"""
        try:
            data = obj_in.model_dump()
            # Map metadata to meta field for database
            if "metadata" in data:
                data["meta"] = data.pop("metadata")

            db_obj = self.model(**data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created Model {db_obj.id}")
            return db_obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating Model: {str(e)}")
            raise

    async def get_by_name(self, name: str) -> Optional[Model]:
        """Get latest model by name"""
        try:
            return (
                self.db.query(Model)
                .filter(Model.name == name)
                .order_by(Model.created_at.desc())
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting model by name: {str(e)}")
            raise

    async def get_versions(self, name: str, skip: int = 0, limit: int = 10) -> List[Model]:
        """Get all versions of a model"""
        try:
            return (
                self.db.query(Model)
                .filter(Model.name == name)
                .order_by(Model.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting model versions: {str(e)}")
            raise

    async def promote(
        self,
        name: str,
        version: str,
        stage: str,
        reason: Optional[str] = None,
        promoted_by: Optional[str] = None,
    ) -> Optional[Model]:
        """Promote a model to a new stage and record promotion history."""
        try:
            model = (
                self.db.query(Model).filter(Model.name == name, Model.version == version).first()
            )

            if not model:
                return None

            current_stage = model.stage
            if current_stage == stage:
                logger.info(f"Model {name}/{version} is already in stage {stage}")
                return model

            existing = (
                self.db.query(Model)
                .filter(Model.name == name, Model.stage == stage, Model.id != model.id)
                .first()
            )

            previous_model_id = None
            if existing:
                previous_model_id = existing.id
                existing.stage = "staging" if stage == "production" else "dev"
                self.db.add(existing)

            model.stage = stage
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)

            promotion_service = ModelPromotionService(self.db)
            promotion_data = ModelPromotionCreate(
                model_id=model.id,
                from_stage=current_stage,
                to_stage=stage,
                reason=reason,
                promoted_by=promoted_by,
                previous_model_id=previous_model_id,
            )
            await promotion_service.create(promotion_data)

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

    async def rollback(self, name: str, version: str) -> Optional[Model]:
        """Rollback a model by reverting to the previous model in the same stage."""
        try:
            current = (
                self.db.query(Model)
                .filter(
                    Model.name == name,
                    Model.version == version,
                )
                .first()
            )

            if not current:
                return None

            from khops.db.models.model_promotion import ModelPromotion

            last_promotion = (
                self.db.query(ModelPromotion)
                .filter(ModelPromotion.model_id == current.id)
                .order_by(ModelPromotion.promoted_at.desc())
                .first()
            )

            if last_promotion and last_promotion.previous_model_id:
                previous = (
                    self.db.query(Model)
                    .filter(Model.id == last_promotion.previous_model_id)
                    .first()
                )

                if previous:
                    previous.stage = current.stage
                    current.stage = "archived"
                    self.db.add(previous)
                    self.db.add(current)
                    self.db.commit()
                    self.db.refresh(previous)
                    logger.info(f"Rolled back model {name} to version {previous.version}")
                    return previous

            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error rolling back model: {str(e)}")
            raise

    async def retire(self, name: str, version: str) -> Optional[Model]:
        """Retire a model by marking it as archived."""
        try:
            model = (
                self.db.query(Model)
                .filter(
                    Model.name == name,
                    Model.version == version,
                )
                .first()
            )

            if not model:
                return None

            model.stage = "archived"
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            logger.info(f"Retired model {name}/{version}")
            return model
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error retiring model: {str(e)}")
            raise
