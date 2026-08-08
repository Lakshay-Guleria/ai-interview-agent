"""
curriculum_matcher: pure, deterministic logic — NO LLM calls here.

This is intentional. Deciding "did this candidate master Embeddings?" from
their mission pass/fail/skip history is a data-classification problem with
a clear right answer, not a judgement call that benefits from an LLM's
flexibility. Keeping it deterministic means:
  1. It's trivially unit-testable (no mocking an API).
  2. It's free and instant — runs on every request with zero latency/cost.
  3. The interview_planner and question_generator downstream can trust its
     output completely, rather than treating it as another noisy signal.

The LLM's job starts one layer up, in question_generator: turning "topic X,
mastery level WEAK" into actual interview-question wording.
"""
from models.candidate import Candidate
from models.curriculum import Curriculum
from models.mastery import MasteryLevel, TopicMastery


def _classify(mastered: list[int], struggled: list[int], skipped: list[int]) -> tuple[MasteryLevel, str]:
    """
    Scoring rationale:
      - An explicit skip is the strongest negative signal available (the
        candidate chose not to engage), so any skip caps the level at WEAK
        regardless of how well other days in the module went.
      - Otherwise, mastery is judged by the ratio of mastered vs struggled
        days among days the candidate actually attempted.
      - No attempted days at all -> UNKNOWN, never WEAK. We should not
        penalize a candidate for material we have no evidence about; the
        planner treats UNKNOWN as "ask a foundational-level question to
        find out," not "assume they're weak here."
    """
    attempted = mastered + struggled
    total_attempted = len(attempted)

    if skipped:
        return (
            MasteryLevel.WEAK,
            f"Skipped {len(skipped)} day(s) in this module ({skipped}) — treated as a gap regardless of other results.",
        )

    if total_attempted == 0:
        return MasteryLevel.UNKNOWN, "No mission attempts recorded in this module's day range."

    mastered_ratio = len(mastered) / total_attempted

    if mastered_ratio == 1.0:
        return MasteryLevel.STRONG, f"Passed all {len(mastered)} attempted day(s) in this module, no struggles."
    if mastered_ratio >= 0.6:
        return (
            MasteryLevel.MODERATE,
            f"Passed {len(mastered)}/{total_attempted} attempted day(s); some friction (struggled: {struggled}).",
        )
    return (
        MasteryLevel.WEAK,
        f"Only passed {len(mastered)}/{total_attempted} attempted day(s); struggled on {struggled}.",
    )


def match_candidate_to_curriculum(candidate: Candidate, curriculum: Curriculum) -> list[TopicMastery]:
    """
    For every module in the curriculum (in module order), classify the
    candidate's mastery using only the days that fall in that module's
    range. Returns one TopicMastery per module — this list, in order, is
    the direct input to interview_planner in the next step.
    """
    results: list[TopicMastery] = []

    for module in curriculum.modules:
        start_day, end_day = module.days
        days_in_module = range(start_day, end_day + 1)

        mastered = sorted(d for d in candidate.mastered_days if d in days_in_module)
        struggled = sorted(d for d in candidate.struggled_days if d in days_in_module)
        skipped = sorted(d for d in candidate.skipped_days if d in days_in_module)

        recorded_days = {m.day for m in candidate.missions if m.day in days_in_module}
        unattempted = sorted(set(days_in_module) - recorded_days)

        level, rationale = _classify(mastered, struggled, skipped)

        results.append(
            TopicMastery(
                module_n=module.n,
                topic=module.title,
                day_range=(start_day, end_day),
                mastered_days=mastered,
                struggled_days=struggled,
                skipped_days=skipped,
                unattempted_days=unattempted,
                mastery_level=level,
                rationale=rationale,
            )
        )

    return results
