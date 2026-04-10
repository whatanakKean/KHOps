"""Schemas for model promotion audit history."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelPromotionBase(BaseModel):
    model_id: int
    from_stage: str = Field(..., min_length=1, max_length=50)
    to_stage: str = Field(..., min_length=1, max_length=50)
    reason: Optional[str] = None
    promoted_by: Optional[str] = None
    previous_model_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ModelPromotionCreate(ModelPromotionBase):
    pass


class ModelPromotionResponse(ModelPromotionBase):
    id: int
    promoted_at: datetime
