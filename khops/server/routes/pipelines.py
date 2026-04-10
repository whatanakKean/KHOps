"""Route handlers for pipelines"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from khops.server.dependencies import get_db
from khops.server.schemas.pipeline import PipelineCreate, PipelineResponse, PipelineUpdate, PipelineListResponse
from khops.server.services.pipeline_service import PipelineService
from khops.server.services.run_service import RunService
from khops.db.models.run import Run

router = APIRouter()


@router.get("/pipelines", response_model=PipelineListResponse)
async def list_pipelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all pipelines with pagination"""
    try:
        service = PipelineService(db)
        pipelines, total = await service.list_pipelines(skip=skip, limit=limit)
        return PipelineListResponse(
            pipelines=pipelines,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipelines/create", response_model=PipelineResponse)
async def create_pipeline(
    pipeline_in: PipelineCreate,
    db: Session = Depends(get_db),
):
    """Create a new pipeline"""
    try:
        service = PipelineService(db)
        pipeline = await service.create(pipeline_in)
        return pipeline
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating pipeline: {str(e)}")


@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
):
    """Get specific pipeline details"""
    try:
        service = PipelineService(db)
        pipeline = await service.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return pipeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
):
    """Execute a pipeline"""
    try:
        # Verify pipeline exists
        service = PipelineService(db)
        pipeline = await service.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        # Create a new run
        from khops.server.schemas.run import RunCreate
        run_service = RunService(db)
        run_in = RunCreate(pipeline_id=pipeline_id, status="running")
        run = await run_service.create(run_in)
        
        return {
            "pipeline_id": pipeline_id,
            "run_id": run.id,
            "status": "running",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing pipeline: {str(e)}")
