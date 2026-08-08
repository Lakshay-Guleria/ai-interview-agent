"""
App entrypoint. Wires concrete implementations into the orchestrator, then hands
the orchestrator to the route module.

Run with: uvicorn main:app --reload --port 8000
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import interview as interview_routes
from llm.client import FakeLLMClient, GroqLLMClient
from memory.in_memory_store import InMemorySessionStore
from models.candidate import Candidate
from models.curriculum import Curriculum
from services.interview_orchestrator import InterviewOrchestrator
from utils.config import settings

app = FastAPI(title="AI Interview Agent")

# UPDATED: Allow all origins so Vercel can make requests without CORS block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_routes.router)


def _resolve_data_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    backend_dir = Path(__file__).resolve().parent
    project_root = backend_dir.parent
    for base in (Path.cwd(), backend_dir, project_root):
        resolved = (base / path).resolve()
        if resolved.exists():
            return resolved

    return (backend_dir / path).resolve()


@app.on_event("startup")
async def startup() -> None:
    curriculum = Curriculum.load(str(_resolve_data_path(settings.curriculum_path)))
    with open(_resolve_data_path(settings.candidates_path), "r", encoding="utf-8") as f:
        candidates = [Candidate.model_validate(raw) for raw in json.load(f)["candidates"]]

    session_store = InMemorySessionStore()
    
    # Check for GROQ_API_KEY in environment or pydantic settings
    groq_key = os.getenv("GROQ_API_KEY") or getattr(settings, "groq_api_key", "")
    
    if groq_key:
        llm = GroqLLMClient()
    else:
        llm = FakeLLMClient()

    orchestrator = InterviewOrchestrator(session_store=session_store, llm=llm, curriculum=curriculum)
    interview_routes.set_orchestrator(orchestrator)
    interview_routes.set_candidates(candidates)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "AI Interview Agent API is running",
        "docs": "Visit /docs to see available endpoints"
    }