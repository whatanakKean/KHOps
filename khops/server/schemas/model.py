"""Model API Schemas"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ModelBase(BaseModel):
    """Base model schema"""

    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    stage: str = Field("dev", pattern="^(dev|staging|production)$")

    model_config = ConfigDict(from_attributes=True)


class ModelCreate(ModelBase):
    """Schema for creating a model"""

    project_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    run_id: Optional[int] = None
    path: Optional[str] = None
    framework: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[list[str]] = None


class ModelUpdate(BaseModel):
    """Schema for updating a model"""

    stage: Optional[str] = Field(None, pattern="^(dev|staging|production)$")
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ModelResponse(ModelBase):
    """Schema for model response"""

    id: int
    project_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    run_id: Optional[int] = None
    api_port: Optional[int] = None
    path: Optional[str] = None
    framework: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="meta")
    tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ModelListResponse(BaseModel):
    """Schema for list response"""

    models: list[ModelResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10
