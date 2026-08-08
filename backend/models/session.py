"""
The InterviewSession is the single source of truth for one interview.

Design intent: the API layer never holds state in Python variables between
requests (that would break under multiple workers/restarts). Every request
loads a full InterviewSession from the SessionStore by sessionId, mutates
it via the orchestrator, and saves it back. This file defines exactly what
"the state of an interview" means, so that contract is explicit instead of
implicit in scattered dict keys.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from models.candidate import Candidate


class DifficultyLevel(str, Enum):
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    STAFF = "STAFF"


class PlanItemStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class PlanItem(BaseModel):
    """
    One topic on the interview plan. This is produced by the
    interview_planner service (deterministic, not LLM) and consumed by
    the question_generator (LLM) and orchestrator.
    """
    topic: str                       # e.g. "Embeddings & Vector Search"
    anchor_days: list[int]           # curriculum days this topic covers
    mastery_hint: str                # "MASTERED" | "STRUGGLED" | "SKIPPED" — informs question angle
    status: PlanItemStatus = PlanItemStatus.PENDING
    max_follow_ups: int = 2          # cap so one topic can't consume the whole interview


class Score(BaseModel):
    """Per-answer scoring, per your spec's four dimensions."""
    correctness: int = Field(ge=1, le=5)
    depth: int = Field(ge=1, le=5)
    communication: int = Field(ge=1, le=5)
    confidence: int = Field(ge=1, le=5)
    rationale: str = ""

    @property
    def average(self) -> float:
        return round((self.correctness + self.depth + self.communication + self.confidence) / 4, 2)


class TurnRole(str, Enum):
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"


class Turn(BaseModel):
    """One message in the transcript."""
    role: TurnRole
    content: str
    topic: Optional[str] = None
    score: Optional[Score] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterviewStage(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class InterviewSession(BaseModel):
    session_id: str
    candidate: Candidate
    difficulty: DifficultyLevel

    plan: list[PlanItem] = Field(default_factory=list)
    current_plan_index: int = 0
    follow_ups_asked_current_topic: int = 0

    transcript: list[Turn] = Field(default_factory=list)
    stage: InterviewStage = InterviewStage.NOT_STARTED

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def current_plan_item(self) -> Optional[PlanItem]:
        if 0 <= self.current_plan_index < len(self.plan):
            return self.plan[self.current_plan_index]
        return None

    @property
    def is_last_topic(self) -> bool:
        return self.current_plan_index >= len(self.plan) - 1

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
