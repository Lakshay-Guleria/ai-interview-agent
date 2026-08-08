"""
answer_evaluator: scores a candidate's answer and decides FOLLOW_UP vs
NEXT_TOPIC. Also generates the follow-up question text when needed, since
that generation always needs the evaluation's rationale as input (tightly
coupled -- no value in separating into two services).
"""
from enum import Enum

from llm.client import LLMClient
from models.session import DifficultyLevel, Score
from prompts.evaluation_prompt import build_evaluation_prompt
from prompts.followup_prompt import build_followup_prompt
from prompts.system_prompt import SYSTEM_PROMPT
from utils.llm_json import parse_llm_json


class EvaluationDecision(str, Enum):
    FOLLOW_UP = "FOLLOW_UP"
    NEXT_TOPIC = "NEXT_TOPIC"


async def evaluate_answer(
    *,
    topic: str,
    question: str,
    answer: str,
    difficulty: DifficultyLevel,
    follow_ups_used: int,
    max_follow_ups: int,
    llm: LLMClient,
) -> tuple[Score, EvaluationDecision, str]:
    """Returns (score, decision, rationale). Rationale is passed on to the
    follow-up generator if decision == FOLLOW_UP; never shown to candidate."""
    prompt = build_evaluation_prompt(
        topic=topic,
        question=question,
        answer=answer,
        difficulty=difficulty,
        follow_ups_used=follow_ups_used,
        max_follow_ups=max_follow_ups,
    )
    raw = await llm.complete(SYSTEM_PROMPT, prompt, json_mode=True)
    data = parse_llm_json(raw)

    score = Score(
        correctness=int(data["correctness"]),
        depth=int(data["depth"]),
        communication=int(data["communication"]),
        confidence=int(data["confidence"]),
        rationale=data.get("rationale", ""),
    )
    decision = EvaluationDecision(data["decision"])
    return score, decision, data.get("rationale", "")


async def generate_followup_question(
    *,
    topic: str,
    difficulty: DifficultyLevel,
    previous_question: str,
    previous_answer: str,
    evaluation_rationale: str,
    llm: LLMClient,
) -> str:
    prompt = build_followup_prompt(
        topic=topic,
        difficulty=difficulty,
        previous_question=previous_question,
        previous_answer=previous_answer,
        evaluation_rationale=evaluation_rationale,
    )
    text = await llm.complete(SYSTEM_PROMPT, prompt)
    return text.strip()
