"""
Builds the prompt for generating a follow-up question, once the evaluator
has decided FOLLOW_UP. Separate from question_prompt.py because a follow-up
must reference the candidate's actual prior answer (per spec example:
"You mentioned vectors. How is cosine similarity used during retrieval?"),
which an opening question never does.

TODO (Codex): tune wording.
"""
from models.session import DifficultyLevel


def build_followup_prompt(
    *,
    topic: str,
    difficulty: DifficultyLevel,
    previous_question: str,
    previous_answer: str,
    evaluation_rationale: str,
) -> str:
    return f"""Generate a natural follow-up question, continuing this exchange.

Topic: {topic}
Target difficulty: {difficulty.value}
Previous question: {previous_question}
Candidate's answer: {previous_answer}
Why we're following up (internal, don't reveal): {evaluation_rationale}

Requirements:
- Reference something SPECIFIC the candidate said in their answer.
- Push for the gap identified above (more depth, a concrete example, or
  clarification of something vague/incorrect).
- Keep it to one sentence if possible, two max.

Return ONLY the follow-up question text, nothing else.
"""
