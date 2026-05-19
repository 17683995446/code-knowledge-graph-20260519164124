from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ProjectCreate, ProjectResponse, SyncResponse, StatsResponse
from ..database import db
from ..services import engine

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
async def get_projects():
    return db.get_projects()

@router.post("", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    try:
        project_id = db.create_project(project.name, project.path)
        return db.get_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    db.delete_project(project_id)
    return {"message": "项目已删除"}

@router.post("/{project_id}/sync", response_model=SyncResponse)
async def sync_project(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    result = engine.sync_project(project_id)
    return SyncResponse(**result)

@router.get("/{project_id}/stats", response_model=StatsResponse)
async def get_project_stats(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return db.get_stats(project_id)
