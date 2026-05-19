from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import projects_router, graph_router, chat_router

app = FastAPI(title="Code Knowledge Graph API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(graph_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {
        "message": "Code Knowledge Graph API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
