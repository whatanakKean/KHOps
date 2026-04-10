"""Pipeline API Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class PipelineBase(BaseModel):
    """Base pipeline schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    definition: Dict[str, Any] = Field(..., description="Pipeline YAML as JSON/dict")

    model_config = ConfigDict(from_attributes=True)


class PipelineCreate(PipelineBase):
    """Schema for creating a pipeline"""

    pass


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline"""

    description: Optional[str] = Field(None, max_length=1000)
    definition: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class PipelineResponse(PipelineBase):
    """Schema for pipeline response"""

    id: int
    created_at: datetime
    updated_at: datetime


class PipelineListResponse(BaseModel):
    """Schema for list response"""

    pipelines: list[PipelineResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10
