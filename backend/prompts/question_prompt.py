"""
Builds the user-prompt for generating the opening question on a new topic.

The deterministic planner decides which studied topic is next. This prompt
then asks the LLM to write the actual interviewer question for that topic.
"""
from models.mastery import MasteryLevel
from models.session import DifficultyLevel


def build_question_prompt(
    *,
    topic: str,
    difficulty: DifficultyLevel,
    mastery_hint: MasteryLevel | str,
    candidate_role: str,
    studied_curriculum_context: list[str],
) -> str:
    mastery_note = {
        "STRONG": "The candidate has demonstrated mastery here; ask something that verifies real depth, not just recall.",
        "MODERATE": "The candidate mostly succeeded here with some friction; verify their understanding is solid.",
        "WEAK": "The candidate struggled or skipped this topic; start foundational, then let follow-ups probe the gap.",
    }.get(mastery_hint if isinstance(mastery_hint, str) else mastery_hint.value, "")

    studied_lines = "\n".join(f"- {item}" for item in studied_curriculum_context) or "- No specific day context available."

    return f"""Generate the FIRST interview question on this topic.

Topic: {topic}
Candidate role: {candidate_role}
Target difficulty: {difficulty.value}
Candidate studied curriculum context:
{studied_lines}
{mastery_note}

The question must be based on the studied curriculum context above. Do not ask
random topics outside this candidate's plan. Ask one natural technical question
that a senior engineer would use to start this topic.

Return ONLY the question text, nothing else — no preamble, no "Question 1:" prefix.
"""
