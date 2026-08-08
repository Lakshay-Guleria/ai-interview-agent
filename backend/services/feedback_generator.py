"""
feedback_generator: called once, when the orchestrator marks the session
COMPLETED. Turns the full transcript + scores into the Feedback wire model.
"""

from llm.client import LLMClient
from models.api_schemas import Feedback
from models.session import InterviewSession
from prompts.feedback_prompt import build_feedback_prompt
from prompts.system_prompt import SYSTEM_PROMPT
from utils.llm_json import parse_llm_json


async def generate_feedback(session: InterviewSession, llm: LLMClient) -> Feedback:
    prompt = build_feedback_prompt(session)
    raw = await llm.complete(SYSTEM_PROMPT, prompt, json_mode=True)
    data = parse_llm_json(raw)

    return Feedback(
        summary=data["summary"],
        strengths=data.get("strengths", []),
        gaps=data.get("gaps", []),
        next=data.get("next", []),
    )
