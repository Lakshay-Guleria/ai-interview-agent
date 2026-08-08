"""
InterviewOrchestrator: the brain. The API route stays a thin controller;
ALL interview logic/state transitions live here. This is the one class
that knows the full turn-by-turn flow:

  1. No session yet -> start interview: build plan, ask first question.
  2. Session exists, candidate answers -> evaluate -> FOLLOW_UP or NEXT_TOPIC.
  3. NEXT_TOPIC + more topics left -> ask opening question on next topic.
  4. NEXT_TOPIC + no topics left -> mark COMPLETED, generate feedback.

Depends only on abstractions (SessionStore, LLMClient, Curriculum) injected
at construction — no direct instantiation of OpenAI/dict-store here. This
is the dependency-injection seam mentioned in the architecture doc.

TODO (Codex): this file has the full control flow already — mainly needs
the TODO-marked spots in question_generator/answer_evaluator/feedback_generator
wired to a real LLM to become fully functional. Add logging/error handling
around LLM calls (timeouts, malformed JSON) here or in those services.
"""
from models.api_schemas import InterviewRequest, InterviewResponse
from models.candidate import Candidate
from models.curriculum import Curriculum
from models.session import InterviewSession, InterviewStage, PlanItemStatus, Turn, TurnRole
from services.answer_evaluator import EvaluationDecision, evaluate_answer, generate_followup_question
from services.curriculum_matcher import match_candidate_to_curriculum
from services.feedback_generator import generate_feedback
from services.interview_planner import build_interview_plan
from services.question_generator import generate_opening_question
from utils.difficulty import infer_difficulty
from llm.client import LLMClient
from memory.session_store import SessionStore


class InterviewOrchestrator:
    def __init__(self, session_store: SessionStore, llm: LLMClient, curriculum: Curriculum):
        self._store = session_store
        self._llm = llm
        self._curriculum = curriculum

    async def handle_turn(self, request: InterviewRequest) -> InterviewResponse:
        session = await self._store.get(request.sessionId)

        if session is None:
            if request.candidate is None:
                raise ValueError("First call for a new sessionId must include `candidate`.")
            return await self._start_interview(request.sessionId, request.candidate)

        if request.message is None:
            raise ValueError("Ongoing interview calls must include `message`.")

        if session.stage == InterviewStage.COMPLETED:
            return InterviewResponse(reply="This interview session is already complete.", done=True)

        return await self._continue_interview(session, request.message)

    async def _start_interview(self, session_id: str, candidate: Candidate) -> InterviewResponse:
        mastery = match_candidate_to_curriculum(candidate, self._curriculum)
        plan = build_interview_plan(mastery)
        difficulty = infer_difficulty(candidate)
        if not plan:
            raise ValueError("Candidate has no attempted curriculum topics to interview against.")

        session = InterviewSession(
            session_id=session_id,
            candidate=candidate,
            difficulty=difficulty,
            plan=plan,
            stage=InterviewStage.IN_PROGRESS,
        )

        question = await self._ask_opening_question(session)
        await self._store.save(session)
        return InterviewResponse(reply=question, done=False)

    async def _continue_interview(self, session: InterviewSession, message: str) -> InterviewResponse:
        current_item = session.current_plan_item
        if current_item is None:
            # Defensive: shouldn't happen if stage management is correct.
            raise RuntimeError("No current plan item but interview not marked COMPLETED.")

        last_question = session.transcript[-1].content if session.transcript else ""
        session.transcript.append(Turn(role=TurnRole.CANDIDATE, content=message, topic=current_item.topic))

        score, decision, rationale = await evaluate_answer(
            topic=current_item.topic,
            question=last_question,
            answer=message,
            difficulty=session.difficulty,
            follow_ups_used=session.follow_ups_asked_current_topic,
            max_follow_ups=current_item.max_follow_ups,
            llm=self._llm,
        )
        session.transcript[-1].score = score

        if decision == EvaluationDecision.FOLLOW_UP:
            session.follow_ups_asked_current_topic += 1
            followup = await generate_followup_question(
                topic=current_item.topic,
                difficulty=session.difficulty,
                previous_question=last_question,
                previous_answer=message,
                evaluation_rationale=rationale,
                llm=self._llm,
            )
            session.transcript.append(Turn(role=TurnRole.INTERVIEWER, content=followup, topic=current_item.topic))
            await self._store.save(session)
            return InterviewResponse(reply=followup, done=False)

        # NEXT_TOPIC
        current_item.status = PlanItemStatus.COMPLETED
        session.follow_ups_asked_current_topic = 0

        if session.is_last_topic:
            session.stage = InterviewStage.COMPLETED
            feedback = await generate_feedback(session, self._llm)
            await self._store.save(session)
            return InterviewResponse(
                reply="That wraps up our interview. Thanks for your time — here's your feedback.",
                done=True,
                feedback=feedback,
            )

        session.current_plan_index += 1
        question = await self._ask_opening_question(session)
        await self._store.save(session)
        return InterviewResponse(reply=question, done=False)

    async def _ask_opening_question(self, session: InterviewSession) -> str:
        plan_item = session.current_plan_item
        plan_item.status = PlanItemStatus.IN_PROGRESS
        question = await generate_opening_question(
            plan_item=plan_item,
            difficulty=session.difficulty,
            candidate_role=session.candidate.member.jobRole,
            curriculum=self._curriculum,
            llm=self._llm,
        )
        session.transcript.append(Turn(role=TurnRole.INTERVIEWER, content=question, topic=plan_item.topic))
        return question
