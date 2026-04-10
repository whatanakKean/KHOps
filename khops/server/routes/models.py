"""Route handlers for model registry"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from khops.server.dependencies import get_db
from khops.server.schemas.model import ModelCreate, ModelResponse, ModelUpdate, ModelListResponse
from khops.server.services.model_service import ModelService

router = APIRouter()


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all registered models with pagination"""
    try:
        service = ModelService(db)
        models, total = await service.list_models(skip=skip, limit=limit)
        return ModelListResponse(
            models=models,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/register", response_model=ModelResponse)
async def register_model(
    model_in: ModelCreate,
    db: Session = Depends(get_db),
):
    """Register a new model"""
    try:
        service = ModelService(db)
        model = await service.create(model_in)
        return model
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error registering model: {str(e)}")


@router.get("/models/{model_name}", response_model=ModelResponse)
async def get_model(
    model_name: str,
    db: Session = Depends(get_db),
):
    """Get latest version of a model"""
    try:
        service = ModelService(db)
        model = await service.get_by_name(model_name)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}/versions", response_model=List[ModelResponse])
async def get_model_versions(
    model_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all versions of a model"""
    try:
        service = ModelService(db)
        versions = await service.get_versions(model_name, skip=skip, limit=limit)
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/promote", response_model=ModelResponse)
async def promote_model(
    model_name: str,
    version: str = Query(...),
    stage: str = Query(..., pattern="^(dev|staging|production)$"),
    db: Session = Depends(get_db),
):
    """Promote model to a new stage"""
    try:
        service = ModelService(db)
        model = await service.promote(model_name, version, stage)
        if not model:
            raise HTTPException(status_code=404, detail="Model version not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error promoting model: {str(e)}")
