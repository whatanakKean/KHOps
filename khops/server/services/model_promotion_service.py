"""Service layer for model promotion history."""

from typing import List
from sqlalchemy.orm import Session
import logging
from khops.db.models.model_promotion import ModelPromotion
from khops.server.schemas.model_promotion import ModelPromotionCreate
from khops.server.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ModelPromotionService(
    BaseService[ModelPromotion, ModelPromotionCreate, ModelPromotionCreate]
):
    """Service for model promotion audit history."""

    def __init__(self, db: Session):
        super().__init__(db, ModelPromotion)

    async def list_promotions(
        self, model_id: int, skip: int = 0, limit: int = 10
    ) -> List[ModelPromotion]:
        try:
            return await self.get_all(skip=skip, limit=limit, filters={"model_id": model_id})
        except Exception as e:
            logger.error(f"Error listing promotions for model {model_id}: {str(e)}")
            raise
