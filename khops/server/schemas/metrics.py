"""Metrics API Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class MetricsBase(BaseModel):
    """Base metrics schema"""

    name: str = Field(..., min_length=1, max_length=255)
    value: float
    tags: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class MetricsCreate(MetricsBase):
    """Schema for creating metrics"""

    run_id: int


class MetricsUpdate(BaseModel):
    """Schema for updating metrics"""

    value: Optional[float] = None
    tags: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class MetricsResponse(MetricsBase):
    """Schema for metrics response"""

    id: int
    timestamp: datetime
    run_id: int


class MetricsListResponse(BaseModel):
    """Schema for list response"""

    metrics: list[MetricsResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10
