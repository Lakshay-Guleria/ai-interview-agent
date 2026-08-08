"""
interview_planner: turns a list[TopicMastery] into the ordered list[PlanItem]
that becomes InterviewSession.plan.

Like curriculum_matcher, this is deliberately deterministic — no LLM call.
Per the spec: "our code selects the topic, the LLM generates the wording."
This file IS "our code selects the topic." The LLM's involvement starts one
layer up, in question_generator, which takes a PlanItem + DifficultyLevel
and produces the actual question text.

Selection strategy (balanced mix, confirmed with product owner):
  - UNKNOWN-mastery topics are excluded entirely — we don't grill a
    candidate on material they have no recorded engagement with.
  - Among the rest, we split time roughly evenly between topics the
    candidate is strong in (STRONG/MODERATE — verify real depth, catch
    bluffing) and topics they're weak in (WEAK — probe the actual gap).
  - Final ordering follows curriculum module order (not bucket order), so
    the interview flows the way the candidate actually experienced the
    material, rather than jumping around by mastery level.
"""
import math

from models.curriculum import Curriculum
from models.mastery import MasteryLevel, TopicMastery
from models.session import PlanItem, PlanItemStatus

# Cap on total topics per interview. Mirrors the 8-question example in the
# spec. Kept as a module constant (not hardcoded inline) so it's the one
# place to tune interview length under hackathon time pressure.
MAX_TOPICS = 8

# WEAK topics need more room to probe ("can you elaborate?" follow-ups);
# STRONG topics need less — we're verifying, not teaching.
FOLLOW_UPS_BY_LEVEL = {
    MasteryLevel.STRONG: 1,
    MasteryLevel.MODERATE: 2,
    MasteryLevel.WEAK: 2,
}


def _select_balanced(available: list[TopicMastery], max_topics: int) -> list[TopicMastery]:
    """Pick up to max_topics, split as evenly as possible between the
    'confident' bucket (STRONG/MODERATE) and the 'gap' bucket (WEAK),
    preserving each bucket's original (curriculum) order when truncating."""
    confident = [t for t in available if t.mastery_level in (MasteryLevel.STRONG, MasteryLevel.MODERATE)]
    gaps = [t for t in available if t.mastery_level == MasteryLevel.WEAK]

    if len(available) <= max_topics:
        return available

    gap_quota = math.ceil(max_topics / 2)
    confident_quota = max_topics - gap_quota

    # If one bucket is smaller than its quota, let the other bucket absorb
    # the slack rather than returning fewer than max_topics topics.
    if len(gaps) < gap_quota:
        confident_quota += gap_quota - len(gaps)
        gap_quota = len(gaps)
    if len(confident) < confident_quota:
        gap_quota += confident_quota - len(confident)
        confident_quota = len(confident)

    selected_ids = {id(t) for t in confident[:confident_quota]} | {id(t) for t in gaps[:gap_quota]}
    return [t for t in available if id(t) in selected_ids]


def build_interview_plan(mastery_list: list[TopicMastery], max_topics: int = MAX_TOPICS) -> list[PlanItem]:
    """
    Main entry point. Takes the matcher's output, filters + balances +
    orders it, and produces the PlanItem list ready to attach to a fresh
    InterviewSession.
    """
    available = [t for t in mastery_list if t.mastery_level != MasteryLevel.UNKNOWN]
    selected = _select_balanced(available, max_topics)

    # Preserve curriculum (module_n) order for the final plan, regardless
    # of which bucket each topic came from — this is what makes the
    # interview flow feel natural rather than jumpy.
    selected.sort(key=lambda t: t.module_n)

    plan: list[PlanItem] = []
    for topic in selected:
        anchor_days = topic.struggled_days or topic.skipped_days or topic.mastered_days
        plan.append(
            PlanItem(
                topic=topic.topic,
                anchor_days=anchor_days,
                mastery_hint=topic.mastery_level.value,
                status=PlanItemStatus.PENDING,
                max_follow_ups=FOLLOW_UPS_BY_LEVEL[topic.mastery_level],
            )
        )

    return plan
