"""
Builds the prompt for the final interview report, once the interview is
COMPLETED. Consumes the full transcript + all per-answer scores.

TODO (Codex): tune wording; consider truncating transcript if it risks
exceeding context window on long interviews.
"""
from models.session import InterviewSession


FEEDBACK_JSON_SCHEMA_NOTE = """Respond ONLY with a JSON object matching this exact shape:
{
  "summary": "<2-3 sentence overall summary>",
  "strengths": ["<specific strength>", ...],
  "gaps": ["<specific weakness/gap>", ...],
  "next": ["<specific recommendation for what to study/practice next>", ...],
  "overall_score": <float 1-5>,
  "hiring_readiness": "NOT_READY" | "NEEDS_GROWTH" | "READY" | "STRONG_HIRE"
}"""


def build_feedback_prompt(session: InterviewSession) -> str:
    transcript_lines = []
    for turn in session.transcript:
        prefix = "Q" if turn.role.value == "interviewer" else "A"
        score_note = f" [scores: {turn.score.model_dump()}]" if turn.score else ""
        transcript_lines.append(f"{prefix}: {turn.content}{score_note}")

    transcript_text = "\n".join(transcript_lines)

    topics_covered = ", ".join(p.topic for p in session.plan if p.status.value == "COMPLETED")

    return f"""Generate a final interview report for this candidate.

Candidate: {session.candidate.member.name}, {session.candidate.member.jobRole}, \
{session.candidate.member.yearsExperience} years experience.
Difficulty level assessed at: {session.difficulty.value}
Topics covered: {topics_covered}

Full transcript:
{transcript_text}

Be specific — reference actual topics and moments from the transcript, not
generic platitudes.

{FEEDBACK_JSON_SCHEMA_NOTE}
"""
