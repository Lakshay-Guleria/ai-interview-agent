"""
Domain models for the curriculum. Mirrors curriculum.json.

This is loaded once at startup and treated as immutable, read-only
reference data shared across all interview sessions — it never needs
per-session copies.
"""
from typing import Optional

from pydantic import BaseModel


class CurriculumModule(BaseModel):
    n: int
    title: str
    days: list[int]  # [start_day, end_day] inclusive range


class CurriculumDay(BaseModel):
    day: int
    title: str
    type: str  # SETUP | BUILD | LEARN | SHIP_IT | OPTIMIZE | CAPSTONE
    tools: list[str]
    objectives: list[str]


class Curriculum(BaseModel):
    cohort: str
    modules: list[CurriculumModule]
    days: list[CurriculumDay]

    def day_info(self, day: int) -> Optional[CurriculumDay]:
        return next((d for d in self.days if d.day == day), None)

    def module_for_day(self, day: int) -> Optional[CurriculumModule]:
        for module in self.modules:
            start, end = module.days
            if start <= day <= end:
                return module
        return None

    @classmethod
    def load(cls, path: str) -> "Curriculum":
        import json
        with open(path, "r", encoding="utf-8") as f:
            return cls.model_validate(json.load(f))
