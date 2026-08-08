"""
The only HTTP-facing file in the whole system. Deliberately thin: parse
request, call orchestrator, return response. All logic lives in
services/interview_orchestrator.py.
"""
from fastapi import APIRouter, HTTPException

from models.candidate import Candidate
from models.api_schemas import InterviewRequest, InterviewResponse

router = APIRouter()

# Wired up in main.py at startup. For this hackathon-sized app, this keeps
# route signatures simple while the orchestrator itself remains injectable.
_orchestrator = None  # type: ignore
_candidates: list[Candidate] = []


def set_orchestrator(orchestrator) -> None:
    global _orchestrator
    _orchestrator = orchestrator


def set_candidates(candidates: list[Candidate]) -> None:
    global _candidates
    _candidates = candidates


@router.get("/api/candidates", response_model=list[Candidate])
async def list_candidates() -> list[Candidate]:
    return _candidates


@router.post("/api/interview", response_model=InterviewResponse)
async def interview_turn(request: InterviewRequest) -> InterviewResponse:
    if _orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized.")
    try:
        return await _orchestrator.handle_turn(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
