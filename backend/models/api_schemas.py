"""
Wire contracts for POST /api/interview.

Kept deliberately separate from the internal domain models (InterviewSession,
Candidate, etc). The API shape and our internal state shape are allowed to
diverge over time — e.g. we may add internal-only fields to InterviewSession
later — without ever breaking technical-spec.md's contract. Services should
build a Feedback / InterviewTurnResponse from internal state, not return
internal models directly.
"""
from typing import Optional

from pydantic import BaseModel, Field

from models.candidate import Candidate


class InterviewRequest(BaseModel):
    """
    Single endpoint, single request shape, per technical-spec.md.
    - First call (start): sessionId + candidate, no message.
    - Every subsequent call: sessionId + message, no candidate.
    """
    sessionId: str
    candidate: Optional[Candidate] = None
    message: Optional[str] = None


class Feedback(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next: list[str] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None
