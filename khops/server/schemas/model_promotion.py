"""Schemas for model promotion audit history."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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


class ModelPromotionRequest(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    pipeline_id: Optional[int] = None
    project_id: Optional[int] = None
    stage: str = Field(..., pattern="^(dev|staging|production)$")
    reason: Optional[str] = None
    promoted_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ModelPromotionResponse(ModelPromotionBase):
    id: int
    promoted_at: datetime
