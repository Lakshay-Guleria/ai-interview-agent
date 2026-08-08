# AI Interview Agent

## Status

**Fully built & tested (deterministic core):**
- `backend/models/*` — all domain models, validated against real curriculum.json/candidates.json
- `backend/services/curriculum_matcher.py` — candidate mission history -> per-topic mastery (STRONG/MODERATE/WEAK/UNKNOWN)
- `backend/services/interview_planner.py` — mastery -> balanced, ordered interview plan
- `backend/utils/difficulty.py` — candidate profile -> JUNIOR/MID/SENIOR/STAFF
- `backend/services/interview_orchestrator.py` — full state machine control flow (start -> question -> evaluate -> follow-up/next -> feedback)
- `backend/memory/*`, `backend/api/routes/interview.py`, `backend/main.py` — wired end-to-end, smoke-tested with a `FakeLLMClient`

**Templates only — needs real LLM wiring (marked `TODO (Codex)`):**
- `backend/llm/client.py` — implement `OpenAILLMClient.complete()` using the OpenAI SDK
- `backend/services/question_generator.py`, `answer_evaluator.py`, `feedback_generator.py` — already call the `LLMClient` interface correctly; just need `main.py`'s `FakeLLMClient()` swapped for `OpenAILLMClient()` once the client is implemented
- `backend/prompts/*.py` — prompt wording is drafted but should be tuned against real model output
- `frontend/*` — Vite/React/Tailwind/TS scaffold with types matching the API contract, a working chat component, and an API client. Needs: candidate-selection screen (`App.tsx` currently uses a placeholder candidate), polish, loading states, error handling.

## Run order for Codex

1. Implement `backend/llm/client.py::OpenAILLMClient`
2. Swap `FakeLLMClient()` -> `OpenAILLMClient()` in `backend/main.py`
3. `cd backend && pip install -r requirements.txt && cp .env.example .env` (add your `OPENAI_API_KEY`), then `uvicorn main:app --reload --port 8000`
4. Build `frontend/src/components/CandidateSelect.tsx`, wire it into `App.tsx` in place of `PLACEHOLDER_CANDIDATE`
5. `cd frontend && npm install && npm run dev`

## Architecture reference

```
backend/
  models/       - Pydantic domain models (Candidate, Curriculum, InterviewSession, TopicMastery)
  services/      - curriculum_matcher, interview_planner (deterministic, LLM-free)
                   question_generator, answer_evaluator, feedback_generator (LLM-facing)
                   interview_orchestrator (state machine, ties everything together)
  prompts/       - one file per LLM call site
  memory/        - SessionStore interface + InMemorySessionStore impl
  llm/           - LLMClient interface + OpenAI/Fake implementations
  api/routes/    - single POST /api/interview endpoint
  utils/         - config, difficulty inference
frontend/
  src/components/ - InterviewChat.tsx (working), CandidateSelect.tsx (TODO)
  src/lib/api.ts   - fetch wrapper for POST /api/interview
  src/types/api.ts - TS types mirroring backend/models/api_schemas.py
```

Key design principle preserved throughout: **deterministic code decides WHAT
(which topic, which candidate signal to probe), the LLM decides HOW (the
actual question/evaluation wording)**. Don't blur this line when extending —
e.g. don't let the LLM pick which topic comes next; that stays in
`interview_planner.py`.
