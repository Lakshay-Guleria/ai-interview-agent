"""
Thin wrapper around the LLM provider SDK. Every LLM-touching service depends on
THIS interface — keeps provider swap-out and mocking (for tests) trivial.
"""
import json
import os
import re
from abc import ABC, abstractmethod

from utils.config import settings


class LLMClient(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> str:
        """Return the raw text (or JSON string, if json_mode=True) of the
        model's response for a single-turn system+user prompt call."""
        raise NotImplementedError


class GroqLLMClient(LLMClient):
    def __init__(self, model: str = None, temperature: float = None):
        api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "groq_api_key", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required to use GroqLLMClient.")

        from groq import AsyncGroq

        self.model = model or getattr(settings, "llm_model", "llama-3.3-70b-versatile")
        self.temperature = temperature if temperature is not None else getattr(settings, "llm_temperature", 0.7)
        self._client = AsyncGroq(api_key=api_key)

    async def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response.")
        return content


class FakeLLMClient(LLMClient):
    """Deterministic stub for local dev/testing without burning API calls.
    Wire this in via dependency injection when GROQ_API_KEY is unset.

    It still adapts to the candidate answer so local demos exercise the same
    orchestrator flow as the real LLM path.
    """

    async def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> str:
        if json_mode and '"summary"' in user_prompt:
            return json.dumps(
                {
                    "summary": "The candidate showed reasonable technical grounding across the interview, with a few areas that need deeper practice.",
                    "strengths": ["Explains core ideas clearly", "Connects topics to implementation tradeoffs"],
                    "gaps": ["Needs more precision under follow-up pressure"],
                    "next": ["Practice designing a full RAG pipeline aloud", "Review deployment and observability tradeoffs"],
                }
            )
        if json_mode:
            answer = self._extract_field(user_prompt, "Candidate's answer")
            followup_budget = "No follow-up budget remains" not in user_prompt
            word_count = len(answer.split())
            has_tradeoff = self._contains_any(answer, ["tradeoff", "latency", "cost", "scale", "failure", "risk"])
            has_example = self._contains_any(answer, ["example", "for instance", "in production", "when i", "i would"])
            is_vague = word_count < 18 or self._contains_any(answer, ["not sure", "maybe", "basically", "stuff", "things"])

            should_follow_up = followup_budget and (is_vague or not has_tradeoff or not has_example)
            return json.dumps(
                {
                    "correctness": 3 if should_follow_up else 4,
                    "depth": 2 if should_follow_up else 4,
                    "communication": 3,
                    "confidence": 2 if is_vague else 4,
                    "rationale": (
                        "The answer needs a concrete example or tradeoff to verify real understanding."
                        if should_follow_up
                        else "The answer is specific enough to move to the next planned topic."
                    ),
                    "decision": "FOLLOW_UP" if should_follow_up else "NEXT_TOPIC",
                }
            )

        topic = "this topic"
        for line in user_prompt.splitlines():
            if line.startswith("Topic:"):
                topic = line.replace("Topic:", "", 1).strip()
                break

        previous_answer = self._extract_field(user_prompt, "Candidate's answer")
        if previous_answer:
            phrase = " ".join(previous_answer.split()[:8])
            return f"You mentioned '{phrase}'. Can you make that concrete with an example and one tradeoff you would watch for?"

        studied_day = self._first_bullet(user_prompt)
        if studied_day:
            return f"Let's start with {topic}. In {studied_day}, how would you explain the core idea and one practical tradeoff?"
        return f"Let's start with {topic}. How would you explain the core idea and one practical tradeoff?"

    @staticmethod
    def _contains_any(text: str, needles: list[str]) -> bool:
        lowered = text.lower()
        return any(needle in lowered for needle in needles)

    @staticmethod
    def _extract_field(prompt: str, field_name: str) -> str:
        match = re.search(rf"{re.escape(field_name)}:\s*(.*?)(?:\n[A-Z][^:\n]{{2,80}}:|\n\n|$)", prompt, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _first_bullet(prompt: str) -> str:
        for line in prompt.splitlines():
            if line.startswith("- Day "):
                first_sentence = line[2:].split(". ", 1)[0].strip()
                return first_sentence
        return ""