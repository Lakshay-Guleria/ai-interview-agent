"""
question_generator: the LLM-facing counterpart to interview_planner.
Planner already decided WHICH studied topic comes next; this decides HOW to
word the question, calibrated to the candidate and curriculum context.
"""
from llm.client import LLMClient
from models.curriculum import Curriculum
from models.session import DifficultyLevel, PlanItem
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.question_prompt import build_question_prompt


async def generate_opening_question(
    *,
    plan_item: PlanItem,
    difficulty: DifficultyLevel,
    candidate_role: str,
    curriculum: Curriculum,
    llm: LLMClient,
) -> str:
    studied_curriculum_context = []
    for day in plan_item.anchor_days:
        day_info = curriculum.day_info(day)
        if day_info:
            objectives = "; ".join(day_info.objectives[:2])
            tools = ", ".join(day_info.tools[:4])
            studied_curriculum_context.append(
                f"Day {day}: {day_info.title}. Objectives: {objectives}. Tools: {tools}."
            )

    prompt = build_question_prompt(
        topic=plan_item.topic,
        difficulty=difficulty,
        mastery_hint=plan_item.mastery_hint,
        candidate_role=candidate_role,
        studied_curriculum_context=studied_curriculum_context,
    )
    question_text = await llm.complete(SYSTEM_PROMPT, prompt)
    return question_text.strip()
