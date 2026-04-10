"""Route handlers for model serving."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from khops.server.dependencies import get_db
from khops.server.schemas.serving import PredictionRequest, PredictionResponse
from khops.server.services.serving_service import ModelServingService

router = APIRouter()


@router.post("/serve/{model_name}", response_model=PredictionResponse)
async def serve_model(
    model_name: str,
    request: PredictionRequest,
    version: Optional[str] = Query(None, description="Specific model version to use"),
    stage: Optional[str] = Query(
        None, description="Model stage to select (dev, staging, production)"
    ),
    db: Session = Depends(get_db),
):
    """Serve predictions from a registered model."""
    service = ModelServingService(db)
    model = await service.get_model(model_name, version=version, stage=stage)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        loaded_model = service.load_model(model)
        predictions = service.predict(loaded_model, request.features)
        return PredictionResponse(
            model_name=model.name,
            version=model.version,
            stage=model.stage,
            predictions=predictions,
            input_count=len(request.features),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/serve/{model_name}/metadata")
async def serve_model_metadata(
    model_name: str,
    version: Optional[str] = Query(None, description="Specific model version to use"),
    stage: Optional[str] = Query(
        None, description="Model stage to select (dev, staging, production)"
    ),
    db: Session = Depends(get_db),
):
    """Return serving metadata for a registered model."""
    service = ModelServingService(db)
    model = await service.get_model(model_name, version=version, stage=stage)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        metadata = service.get_model_metadata(model)
        return metadata
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/serve/{model_name}/health")
async def serve_model_health(
    model_name: str,
    version: Optional[str] = Query(None, description="Specific model version to use"),
    stage: Optional[str] = Query(
        None, description="Model stage to select (dev, staging, production)"
    ),
    db: Session = Depends(get_db),
):
    """Return health status for a serving model."""
    service = ModelServingService(db)
    model = await service.get_model(model_name, version=version, stage=stage)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return {
        "model_name": model.name,
        "version": model.version,
        "stage": model.stage,
        "status": "available",
        "last_updated": model.updated_at,
    }
