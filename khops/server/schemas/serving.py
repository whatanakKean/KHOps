"""Schemas for model serving endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PredictionRequest(BaseModel):
    """Request body for model inference."""

    features: List[Dict[str, Any]] = Field(
        ..., description="List of feature dictionaries to predict"
    )

    model_config = ConfigDict(from_attributes=True)


class PredictionResponse(BaseModel):
    """Response returned by the model serving endpoint."""

    model_name: str
    version: str
    stage: str
    predictions: List[Any]
    input_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
