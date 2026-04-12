"""Route handlers for model registry operations"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from khops.db.models.model import Model
from khops.db.models.pipeline import Pipeline
from khops.db.models.run import Run
from khops.server.dependencies import get_db
from khops.server.schemas.model import ModelListResponse, ModelResponse
from khops.server.services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/registry/stats")
async def get_registry_stats(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get registry statistics"""
    try:
        total_models = db.query(Model).count()
        models_by_stage = {}
        for stage in ["dev", "staging", "production", "archived"]:
            models_by_stage[stage] = db.query(Model).filter(Model.stage == stage).count()

        total_versions = db.query(Model).count()
        unique_model_names = db.query(Model.name).distinct().count()

        return {
            "total_models": total_models,
            "unique_model_names": unique_model_names,
            "total_versions": total_versions,
            "models_by_stage": models_by_stage,
            "timestamp": (
                db.query(Model).order_by(Model.created_at.desc()).first().created_at
                if total_models > 0
                else None
            ),
        }
    except Exception as e:
        logger.error(f"Error getting registry stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/search", response_model=ModelListResponse)
async def search_models(
    q: Optional[str] = Query(None, min_length=1, description="Search query for model name or tag"),
    stage: Optional[str] = Query(None, pattern="^(dev|staging|production|archived)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ModelListResponse:
    """Search models by name, tags, or stage"""
    try:
        query = db.query(Model)

        if q:
            query = query.filter(Model.name.ilike(f"%{q}%"))

        if stage:
            query = query.filter(Model.stage == stage)

        total = query.count()
        models = query.order_by(Model.created_at.desc()).offset(skip).limit(limit).all()

        return ModelListResponse(
            models=models,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Error searching models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/models/{model_name}/metadata")
async def get_model_metadata(
    model_name: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get comprehensive metadata for a model"""
    try:
        service = ModelService(db)
        model = await service.get_by_name(model_name)

        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        # Get all versions
        versions = await service.get_versions(model_name, skip=0, limit=1000)

        return {
            "name": model_name,
            "current_version": model.version,
            "current_stage": model.stage,
            "total_versions": len(versions),
            "versions": [
                {
                    "version": v.version,
                    "stage": v.stage,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ],
            "metadata": model.meta or {},
            "path": model.path,
            "framework": model.framework,
            "tags": model.tags or [],
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/models/{model_name}/artifacts")
async def get_model_artifacts(
    model_name: str,
    version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get model artifacts and storage information"""
    try:
        service = ModelService(db)

        if version:
            model = (
                db.query(Model)
                .filter(
                    Model.name == model_name,
                    Model.version == version,
                )
                .first()
            )
        else:
            model = await service.get_by_name(model_name)

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        return {
            "model_name": model.name,
            "version": model.version,
            "stage": model.stage,
            "path": model.path,
            "framework": model.framework,
            "size_bytes": model.meta.get("size_bytes") if model.meta else None,
            "hash": model.meta.get("hash") if model.meta else None,
            "metrics": model.metrics or {},
            "created_at": model.created_at,
            "artifact_info": {
                "location": f"file://{model.path}" if model.path.startswith("/") else model.path,
                "framework": model.framework,
                "format": model.meta.get("format", "unknown") if model.meta else "unknown",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model artifacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/models/{model_name}/lineage")
async def get_model_lineage(
    model_name: str,
    version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get model lineage - pipeline and run information"""
    try:
        service = ModelService(db)

        if version:
            model = (
                db.query(Model)
                .filter(
                    Model.name == model_name,
                    Model.version == version,
                )
                .first()
            )
        else:
            model = await service.get_by_name(model_name)

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get pipelines (just list all available)
        pipelines = db.query(Pipeline).limit(50).all()

        return {
            "model_name": model.name,
            "version": model.version,
            "stage": model.stage,
            "framework": model.framework,
            "available_pipelines": len(pipelines),
            "created_at": model.created_at.isoformat() if model.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model lineage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/stages/{stage}", response_model=ModelListResponse)
async def get_models_by_stage(
    stage: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ModelListResponse:
    """Get all models in a specific stage"""
    try:
        if stage not in ["dev", "staging", "production", "archived"]:
            raise HTTPException(status_code=400, detail="Invalid stage")

        query = db.query(Model).filter(Model.stage == stage)
        total = query.count()
        models = query.order_by(Model.created_at.desc()).offset(skip).limit(limit).all()

        return ModelListResponse(
            models=models,
            total=total,
            skip=skip,
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting models by stage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/compare")
async def compare_models(
    model_names: List[str] = Query(..., min_items=2, max_items=5),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Compare multiple models side by side"""
    try:
        comparison = {}
        service = ModelService(db)

        for name in model_names:
            model = await service.get_by_name(name)
            if model:
                comparison[name] = {
                    "version": model.version,
                    "stage": model.stage,
                    "framework": model.framework,
                    "metrics": model.metrics or {},
                    "created_at": model.created_at,
                    "updated_at": model.updated_at,
                }

        return {
            "models": comparison,
            "compared_count": len(comparison),
            "requested_count": len(model_names),
        }
    except Exception as e:
        logger.error(f"Error comparing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/recommendations")
async def get_model_recommendations(
    stage: Optional[str] = Query(None, pattern="^(dev|staging|production)$"),
    metric: str = Query("accuracy", description="Metric to sort by"),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get recommended models based on metrics"""
    try:
        query = db.query(Model)

        if stage:
            query = query.filter(Model.stage == stage)

        models = query.order_by(Model.updated_at.desc()).limit(limit).all()

        recommendations = []
        for model in models:
            if model.metrics and metric in model.metrics:
                recommendations.append(
                    {
                        "name": model.name,
                        "version": model.version,
                        "stage": model.stage,
                        "metric_value": model.metrics[metric],
                        "metric_name": metric,
                        "created_at": model.created_at,
                    }
                )

        # Sort by metric value (descending)
        recommendations.sort(key=lambda x: x.get("metric_value", 0), reverse=True)

        return recommendations[:limit]
    except Exception as e:
        logger.error(f"Error getting model recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/export-metadata")
async def export_model_metadata(
    model_name: str,
    version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Export complete model metadata for external systems"""
    try:
        service = ModelService(db)

        if version:
            model = (
                db.query(Model)
                .filter(
                    Model.name == model_name,
                    Model.version == version,
                )
                .first()
            )
        else:
            model = await service.get_by_name(model_name)

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get promotion history
        from khops.db.models.model_promotion import ModelPromotion

        promotions = (
            db.query(ModelPromotion)
            .filter(ModelPromotion.model_id == model.id)
            .order_by(ModelPromotion.promoted_at.desc())
            .all()
        )

        return {
            "export_metadata": {
                "name": model.name,
                "version": model.version,
                "stage": model.stage,
                "framework": model.framework,
                "path": model.path,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "updated_at": model.updated_at.isoformat() if model.updated_at else None,
                "metrics": model.metrics or {},
                "metadata": model.meta or {},
                "tags": model.tags or [],
                "promotion_history": [
                    {
                        "from_stage": p.from_stage,
                        "to_stage": p.to_stage,
                        "reason": p.reason,
                        "promoted_by": p.promoted_by,
                        "promoted_at": p.promoted_at.isoformat() if p.promoted_at else None,
                    }
                    for p in promotions
                ],
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting model metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
