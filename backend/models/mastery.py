"""
Output shape of curriculum_matcher: candidate mission data collapsed into
one mastery judgement per curriculum module/topic.

This sits between raw Candidate data and the InterviewPlan. Keeping it as
its own model (rather than returning tuples/dicts from the matcher) means
the planner and question_generator get a stable, self-documenting contract
to consume.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MasteryLevel(str, Enum):
    STRONG = "STRONG"          # mastered, no real struggle signal — go hard, push depth
    MODERATE = "MODERATE"      # mostly mastered but with some friction — verify understanding
    WEAK = "WEAK"              # struggled and/or explicitly skipped material — probe gently, check fundamentals
    UNKNOWN = "UNKNOWN"        # no mission record at all in this range — candidate may not have reached it


class TopicMastery(BaseModel):
    module_n: int
    topic: str                     # curriculum module title, used as the plan's "topic" label
    day_range: tuple[int, int]

    mastered_days: list[int]
    struggled_days: list[int]
    skipped_days: list[int]        # explicit skip signal, not "no data"
    unattempted_days: list[int]    # days in range with no mission record at all

    mastery_level: MasteryLevel
    rationale: str                 # human-readable "why" — surfaced in planner logs / debugging

    @property
    def anchor_day(self) -> Optional[int]:
        """
        The single most useful day to ground a question in, in priority
        order: a struggle (richest follow-up material) > a skip (worth
        asking 'why') > a mastery (worth verifying depth) > None (topic
        wasn't attempted at all, question must be generic/foundational).
        """
        if self.struggled_days:
            return self.struggled_days[0]
        if self.skipped_days:
            return self.skipped_days[0]
        if self.mastered_days:
            return self.mastered_days[0]
        return None
