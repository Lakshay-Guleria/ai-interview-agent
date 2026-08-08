"""
Helpers for parsing JSON returned by LLM calls.

Even with provider JSON mode enabled, keeping parsing behind one function
lets services produce clear API errors instead of stack traces if a model or
stub ever returns malformed content.
"""
import json
import re
from typing import Any


_FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def parse_llm_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fenced = _FENCED_JSON_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM returned malformed JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("LLM JSON response must be an object.")

    return data
