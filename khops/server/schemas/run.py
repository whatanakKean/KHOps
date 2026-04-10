"""Run API Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class RunBase(BaseModel):
    """Base run schema"""

    pipeline_id: int
    status: str = Field("pending", pattern="^(pending|running|success|failed|cancelled)$")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logs: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class RunCreate(RunBase):
    """Schema for creating a run"""

    pass


class RunUpdate(BaseModel):
    """Schema for updating a run"""

    status: Optional[str] = Field(None, pattern="^(pending|running|success|failed|cancelled)$")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logs: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class RunResponse(RunBase):
    """Schema for run response"""

    id: int
    created_at: datetime


class RunListResponse(BaseModel):
    """Schema for list response"""

    runs: list[RunResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10
