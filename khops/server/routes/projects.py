"""Route handlers for project management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from khops.server.dependencies import get_db
from khops.server.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse
from khops.server.services.project_service import ProjectService

router = APIRouter()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        service = ProjectService(db)
        projects, total = await service.list_projects(skip=skip, limit=limit)
        return ProjectListResponse(projects=projects, total=total, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/create", response_model=ProjectResponse)
async def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    try:
        service = ProjectService(db)
        project = await service.create(project_in)
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating project: {str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    try:
        service = ProjectService(db)
        project = await service.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
