"""Route handlers for model registry"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from khops.db.models.model import Model
from khops.server.dependencies import get_db
from khops.server.schemas.model import ModelCreate, ModelListResponse, ModelResponse, ModelUpdate
from khops.server.schemas.model_promotion import ModelPromotionRequest, ModelPromotionResponse
from khops.server.services.model_promotion_service import ModelPromotionService
from khops.server.services.model_service import ModelService

router = APIRouter()


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = Query(None, description="Filter models by project id"),
    pipeline_id: Optional[int] = Query(None, description="Filter models by pipeline id"),
    db: Session = Depends(get_db),
):
    """List all registered models with pagination"""
    try:
        service = ModelService(db)
        models, total = await service.list_models(
            skip=skip, limit=limit, project_id=project_id, pipeline_id=pipeline_id
        )
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
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    db: Session = Depends(get_db),
):
    """Get latest version of a model"""
    try:
        service = ModelService(db)
        model = await service.get_by_name(model_name, project_id=project_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}/{version}", response_model=ModelResponse)
async def get_model_version(
    model_name: str,
    version: str,
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    pipeline_id: Optional[int] = Query(None, description="Filter by pipeline id"),
    db: Session = Depends(get_db),
):
    """Get a specific model version"""
    try:
        query = db.query(Model).filter(
            Model.name == model_name,
            Model.version == version,
        )
        if project_id is not None:
            query = query.filter(Model.project_id == project_id)
        if pipeline_id is not None:
            query = query.filter(Model.pipeline_id == pipeline_id)
        model = query.first()
        if not model:
            raise HTTPException(status_code=404, detail="Model version not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}/versions", response_model=List[ModelResponse])
async def get_model_versions(
    model_name: str,
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    pipeline_id: Optional[int] = Query(None, description="Filter by pipeline id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all versions of a model"""
    try:
        service = ModelService(db)
        versions = await service.get_versions(
            model_name,
            project_id=project_id,
            pipeline_id=pipeline_id,
            skip=skip,
            limit=limit,
        )
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/promote", response_model=ModelResponse)
async def promote_model(
    model_name: str,
    promotion_request: ModelPromotionRequest,
    db: Session = Depends(get_db),
):
    """Promote model to a new stage"""
    try:
        service = ModelService(db)
        model = await service.promote(
            model_name,
            promotion_request.version,
            promotion_request.stage,
            pipeline_id=promotion_request.pipeline_id,
            project_id=promotion_request.project_id,
            reason=promotion_request.reason,
            promoted_by=promotion_request.promoted_by,
        )
        if not model:
            raise HTTPException(status_code=404, detail="Model version not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error promoting model: {str(e)}")


@router.get("/models/{model_name}/{version}/history", response_model=List[ModelPromotionResponse])
async def get_model_promotion_history(
    model_name: str,
    version: str,
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    pipeline_id: Optional[int] = Query(None, description="Filter by pipeline id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get promotion history for a specific model version"""
    try:
        model_service = ModelService(db)
        model = await model_service.get_by_name(model_name, project_id=project_id)
        if not model or model.version != version:
            query = db.query(model_service.model).filter(
                model_service.model.name == model_name,
                model_service.model.version == version,
            )
            if project_id is not None:
                query = query.filter(model_service.model.project_id == project_id)
            if pipeline_id is not None:
                query = query.filter(model_service.model.pipeline_id == pipeline_id)
            model = query.first()
        if not model:
            raise HTTPException(status_code=404, detail="Model version not found")

        promotion_service = ModelPromotionService(db)
        promotions = await promotion_service.list_promotions(model.id, skip=skip, limit=limit)
        return promotions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
