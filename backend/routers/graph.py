from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..models import GraphData, SearchResult
from ..database import db

router = APIRouter(prefix="/api", tags=["graph"])

@router.get("/graph/{project_id}", response_model=GraphData)
async def get_graph(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    graph_data = db.get_graph_data(project_id)
    return GraphData(**graph_data)

@router.get("/search", response_model=List[SearchResult])
async def search(
    project_id: int = Query(..., description="项目ID"),
    query: str = Query(..., description="搜索关键词"),
    type_filter: Optional[str] = Query(None, description="类型过滤: type, function")
):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    results = db.search(project_id, query, type_filter)
    return results
