"""
Builds the prompt that scores a candidate's answer AND decides whether to
follow up or move on. This is the adaptive decision point of the interview.
"""
from models.session import DifficultyLevel


EVALUATION_JSON_SCHEMA_NOTE = """Respond ONLY with a JSON object matching this exact shape:
{
  "correctness": <int 1-5>,
  "depth": <int 1-5>,
  "communication": <int 1-5>,
  "confidence": <int 1-5>,
  "rationale": "<one sentence, internal use only, not shown to candidate>",
  "decision": "FOLLOW_UP" | "NEXT_TOPIC"
}"""


def build_evaluation_prompt(
    *,
    topic: str,
    question: str,
    answer: str,
    difficulty: DifficultyLevel,
    follow_ups_used: int,
    max_follow_ups: int,
) -> str:
    budget_note = (
        "No follow-up budget remains for this topic — decision MUST be NEXT_TOPIC."
        if follow_ups_used >= max_follow_ups
        else f"Follow-up budget remaining: {max_follow_ups - follow_ups_used}."
    )

    return f"""Evaluate this candidate's latest answer like a senior technical interviewer.

Topic: {topic}
Target difficulty: {difficulty.value}
Question asked: {question}
Candidate's answer: {answer}

{budget_note}

Score on 4 dimensions (1-5 each):
- correctness: is the answer technically accurate?
- depth: does it show real understanding vs surface-level recall?
- communication: is it clearly articulated?
- confidence: does the candidate sound sure of what they're saying?

Decision policy:
- Choose FOLLOW_UP if the answer is vague, memorized-sounding, partially
  correct, missing an important tradeoff, or gives no concrete example.
- Choose FOLLOW_UP if the candidate mentions a useful concept but you need
  to verify they really understand it.
- Choose NEXT_TOPIC only when the answer is accurate enough for the target
  difficulty and there is no obvious gap worth probing.
- If no follow-up budget remains, choose NEXT_TOPIC.

The next interviewer message will be generated from your decision. Your
rationale must clearly state what to probe if you choose FOLLOW_UP.

{EVALUATION_JSON_SCHEMA_NOTE}
"""
