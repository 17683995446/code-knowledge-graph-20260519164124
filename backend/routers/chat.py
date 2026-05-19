from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ChatResponse
from ..database import db
from ..services import llm_service

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    project = db.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    stats = db.get_stats(request.project_id)
    graph_data = db.get_graph_data(request.project_id)

    project_context = f"""
项目名称: {project['name']}
项目路径: {project['path']}
文件数量: {stats['file_count']}
类型数量: {stats['type_count']}
函数数量: {stats['function_count']}
编程语言分布: {stats['languages']}

代码结构概览:
"""

    types_info = []
    funcs_info = []

    for node in graph_data['nodes'][:50]:
        if node['type'] == 'type':
            types_info.append(f"- {node['kind']}: {node['name']} (文件: {node['file_path']})")
        else:
            funcs_info.append(f"- {node['name']} (文件: {node['file_path']})")

    project_context += "\n类型/类/接口:\n" + "\n".join(types_info[:30])
    project_context += "\n\n函数/方法:\n" + "\n".join(funcs_info[:50])

    messages = [{"role": msg.role, "content": msg.content} for msg in request.history]
    messages.append({"role": "user", "content": request.message})

    answer = llm_service.chat(messages, project_context)

    return ChatResponse(answer=answer, sources=[])
