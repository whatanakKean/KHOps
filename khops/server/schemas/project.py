"""Project API Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 10

    model_config = ConfigDict(from_attributes=True)
