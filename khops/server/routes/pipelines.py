"""Route handlers for pipelines"""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from khops.db.models.run import Run
from khops.pipelines.parser import PipelineParser
from khops.server.dependencies import get_db
from khops.server.schemas.pipeline import (
    PipelineCreate,
    PipelineListResponse,
    PipelineResponse,
    PipelineUpdate,
    PipelineUpload,
)
from khops.server.services.execution_service import PipelineExecutionService
from khops.server.services.pipeline_service import PipelineService
from khops.server.services.run_service import RunService

router = APIRouter()


@router.get("/pipelines", response_model=PipelineListResponse)
async def list_pipelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = Query(None, description="Filter pipelines by project id"),
    db: Session = Depends(get_db),
):
    """List all pipelines with pagination"""
    try:
        service = PipelineService(db)
        pipelines, total = await service.list_pipelines(
            skip=skip, limit=limit, project_id=project_id
        )
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


@router.post("/pipelines/upload", response_model=PipelineResponse)
async def upload_pipeline(
    pipeline_upload: PipelineUpload,
    db: Session = Depends(get_db),
):
    """Upload and register a pipeline from YAML content."""
    try:
        config = PipelineParser.parse_yaml_string(pipeline_upload.yaml_content)
        service = PipelineService(db)
        pipeline = await service.create(
            PipelineCreate(
                name=config.name,
                description=config.description,
                definition=config.model_dump(),
            )
        )
        return pipeline
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading pipeline: {str(e)}")


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


@router.get("/pipelines/{pipeline_name}/versions", response_model=List[PipelineResponse])
async def get_pipeline_versions(
    pipeline_name: str,
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all versions of a named pipeline."""
    try:
        service = PipelineService(db)
        versions = await service.get_versions(
            pipeline_name, project_id=project_id, skip=skip, limit=limit
        )
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Execute a pipeline"""
    try:
        service = PipelineService(db)
        pipeline = await service.get(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")

        from khops.server.schemas.run import RunCreate

        run_service = RunService(db)
        run_in = RunCreate(
            pipeline_id=pipeline_id,
            status="running",
            logs="Pipeline execution registered.",
        )

        run = await run_service.create(run_in)
        background_tasks.add_task(
            PipelineExecutionService.execute_pipeline_background,
            pipeline.definition,
            pipeline_id,
            run.id,
            pipeline.project_id,
        )

        return {
            "pipeline_id": pipeline_id,
            "run_id": run.id,
            "status": "running",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing pipeline: {str(e)}")
