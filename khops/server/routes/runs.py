"""Route handlers for runs"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from khops.server.dependencies import get_db
from khops.server.schemas.run import RunListResponse, RunResponse, RunUpdate
from khops.server.services.run_service import RunService

router = APIRouter()


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all pipeline runs with pagination"""
    try:
        service = RunService(db)
        runs, total = await service.list_runs(skip=skip, limit=limit)
        return RunListResponse(
            runs=runs,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Get specific run details"""
    try:
        service = RunService(db)
        run = await service.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}/logs")
async def get_run_logs(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Get run execution logs"""
    try:
        service = RunService(db)
        run = await service.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return {
            "run_id": run_id,
            "logs": run.logs or "",
            "status": run.status,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}/artifacts")
async def get_run_artifacts(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Get artifact directory and run artifact metadata."""
    try:
        service = RunService(db)
        run = await service.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        artifacts = run.meta or {}
        return {
            "run_id": run_id,
            "status": run.status,
            "artifact_dir": artifacts.get("artifact_dir"),
            "artifact_paths": artifacts.get("artifact_paths", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Cancel a running pipeline"""
    try:
        service = RunService(db)
        run = await service.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        if run.status in {"success", "failed", "cancelled"}:
            raise HTTPException(status_code=400, detail="Cannot cancel completed run")

        # Update run status to cancelled
        update_data = RunUpdate(status="cancelled")
        updated_run = await service.update(run_id, update_data)

        return {
            "run_id": run_id,
            "status": updated_run.status,
            "message": "Run cancelled successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cancelling run: {str(e)}")
