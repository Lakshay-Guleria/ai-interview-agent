"""
Abstract interface for session persistence. The orchestrator depends on
THIS, not on a concrete store — swap InMemorySessionStore for a Redis-
backed one post-hackathon without touching orchestration logic.
"""
from abc import ABC, abstractmethod
from typing import Optional

from models.session import InterviewSession


class SessionStore(ABC):
    @abstractmethod
    async def get(self, session_id: str) -> Optional[InterviewSession]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, session: InterviewSession) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        raise NotImplementedError
