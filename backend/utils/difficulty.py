"""
Infers a DifficultyLevel from the candidate's profile. This is deliberately
a small, standalone utility (not buried in the planner) because it's the
kind of heuristic you'll want to tune fast and independently during the
hackathon without touching planning/orchestration logic.

Signal sources, in order of weight:
  1. Job title seniority keywords — the strongest explicit signal a
     candidate profile gives us.
  2. Years of experience — a coarse but reliable secondary signal.
  3. first_try_rate (from Candidate.signals) — behavioral evidence that
     can push difficulty up/down independent of stated title, e.g. a
     "Software Engineer" who one-shot nearly everything performs like a
     senior in practice.
"""
from models.candidate import Candidate
from models.session import DifficultyLevel

_SENIOR_KEYWORDS = ("senior", "staff", "principal", "distinguished", "lead", "architect")
_JUNIOR_KEYWORDS = ("junior", "intern", "associate", "trainee")


def infer_difficulty(candidate: Candidate) -> DifficultyLevel:
    role = candidate.member.jobRole.lower()
    years = candidate.member.yearsExperience
    first_try_rate = candidate.first_try_rate

    if any(kw in role for kw in _SENIOR_KEYWORDS):
        base = DifficultyLevel.STAFF if "distinguished" in role or "principal" in role else DifficultyLevel.SENIOR
    elif any(kw in role for kw in _JUNIOR_KEYWORDS):
        base = DifficultyLevel.JUNIOR
    elif years >= 8:
        base = DifficultyLevel.SENIOR
    elif years >= 3:
        base = DifficultyLevel.MID
    else:
        base = DifficultyLevel.JUNIOR

    # Behavioral override: strong first-try performance nudges difficulty
    # up one notch even if the title doesn't scream "senior" — e.g. a
    # career-switcher Business Analyst who aces everything on the first
    # try deserves harder questions than the title alone implies.
    ladder = [DifficultyLevel.JUNIOR, DifficultyLevel.MID, DifficultyLevel.SENIOR, DifficultyLevel.STAFF]
    idx = ladder.index(base)

    if first_try_rate >= 0.8 and idx < len(ladder) - 1:
        idx += 1
    elif first_try_rate <= 0.2 and idx > 0:
        idx -= 1

    return ladder[idx]
