"""
Domain models for candidate data.

These mirror the schema in candidates.json exactly. Keeping this file
schema-faithful (rather than "cleaning up" the shape) means loading a
candidate is a pure `Candidate.model_validate(raw_dict)` call with zero
translation logic — one less place for bugs to hide.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class MissionStatus(str, Enum):
    """
    A mission in the raw data can be passed=true, passed=false, or
    skipped=true. Those are three genuinely different signals for an
    interviewer:
      - MASTERED: candidate did the work and passed
      - STRUGGLED: candidate attempted it and failed
      - SKIPPED: candidate never engaged with it at all

    Collapsing these into a single boolean anywhere downstream would
    lose exactly the information an interviewer needs (e.g. "they
    skipped Docker" vs "they tried Docker and failed" call for very
    different follow-up questions).
    """
    MASTERED = "MASTERED"
    STRUGGLED = "STRUGGLED"
    SKIPPED = "SKIPPED"


class Mission(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = None
    skipped: Optional[bool] = None
    attempts: Optional[int] = None

    @computed_field  # type: ignore[misc]
    @property
    def status(self) -> MissionStatus:
        if self.skipped:
            return MissionStatus.SKIPPED
        if self.passed is True:
            return MissionStatus.MASTERED
        return MissionStatus.STRUGGLED

    @computed_field  # type: ignore[misc]
    @property
    def struggled_heavily(self) -> bool:
        """
        3+ attempts to pass is a strong 'shaky fundamentals' signal even
        when the mission was eventually passed. This is exactly the kind
        of nuance a real interviewer would probe on ('I see you passed
        this on your 5th attempt — what was tripping you up?').
        """
        return self.status == MissionStatus.MASTERED and (self.attempts or 0) >= 3


class CandidateSignals(BaseModel):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int


class CandidateMember(BaseModel):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str


class Candidate(BaseModel):
    member: CandidateMember
    missions: list[Mission]
    signals: CandidateSignals

    def mission_for_day(self, day: int) -> Optional[Mission]:
        return next((m for m in self.missions if m.day == day), None)

    @computed_field  # type: ignore[misc]
    @property
    def mastered_days(self) -> set[int]:
        return {m.day for m in self.missions if m.status == MissionStatus.MASTERED}

    @computed_field  # type: ignore[misc]
    @property
    def struggled_days(self) -> set[int]:
        return {m.day for m in self.missions if m.status == MissionStatus.STRUGGLED}

    @computed_field  # type: ignore[misc]
    @property
    def skipped_days(self) -> set[int]:
        return {m.day for m in self.missions if m.status == MissionStatus.SKIPPED}

    @computed_field  # type: ignore[misc]
    @property
    def first_try_rate(self) -> float:
        """Used by difficulty adaptation — a candidate who one-shots most
        missions gets harder questions than one who needed many retries,
        independent of raw years of experience."""
        if self.signals.missionsCompleted == 0:
            return 0.0
        return round(self.signals.missionsFirstTry / self.signals.missionsCompleted, 2)
