from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ProjectCreate(BaseModel):
    name: str
    path: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    created_at: int
    updated_at: int

class StatsResponse(BaseModel):
    file_count: int
    type_count: int
    function_count: int
    languages: Dict[str, int]

class GraphNode(BaseModel):
    id: str
    name: str
    type: str
    kind: str
    file_id: int
    file_path: str
    type_id: Optional[int] = None

class GraphLink(BaseModel):
    source: str
    target: str
    relation: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

class SearchResult(BaseModel):
    id: int
    name: str
    kind: str
    file_path: str
    entity_type: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    project_id: int
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[Dict[str, Any]]] = []

class SyncResponse(BaseModel):
    success: bool
    files_processed: int
    message: str
