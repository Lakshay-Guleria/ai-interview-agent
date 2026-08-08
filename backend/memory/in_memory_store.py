"""
Dict-backed SessionStore. Fine for a single-process hackathon deployment.
NOTE: state is lost on restart and won't work across multiple workers/
processes — if that becomes a problem, swap in a Redis-backed store behind
the same SessionStore interface, no other code changes needed.
"""
from typing import Optional

from memory.session_store import SessionStore
from models.session import InterviewSession


class InMemorySessionStore(SessionStore):
    def __init__(self):
        self._sessions: dict[str, InterviewSession] = {}

    async def get(self, session_id: str) -> Optional[InterviewSession]:
        return self._sessions.get(session_id)

    async def save(self, session: InterviewSession) -> None:
        session.touch()
        self._sessions[session.session_id] = session

    async def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
