# AI Development Prompt Log

This document contains the complete master instruction prompt and sequential prompt log used to architect, build, and refine the **AI Interview Agent**.

---

## 1. Master Architecture & System Specification Prompt

```text
You are a senior AI Engineer and Software Architect.

I am participating in an AI Vibe Coding Hackathon.

Your job is to help me build the entire project from scratch with production-quality architecture.

I don't just want code.

I want you to think like the lead engineer designing the complete system.

Whenever you generate code, explain WHY we are writing it and how it fits into the overall architecture.

==========================================
PROJECT
==========================================

We are building an AI Interview Agent.

The interviewer should behave like a real technical interviewer instead of asking scripted questions.

The AI should:

• Read the curriculum
• Read a candidate profile
• Understand what the candidate learned
• Understand weak and strong areas
• Conduct a conversational interview
• Ask follow-up questions
• Maintain memory
• Evaluate answers
• Generate a final interview report

The interview should feel like interviewing with a senior engineer.

==========================================
FILES PROVIDED
==========================================

I will provide three files.

1. curriculum.json

Contains all 31 learning days.

Each day contains
- day
- title
- objectives
- tools
- type

This is the knowledge base.

-----------------------------------------

2. candidates.json

Contains multiple candidates.

Each candidate contains:

member
- id
- name
- experience
- job role
- education

missions
Each mission contains
- day
- passed
- skipped
- attempts

signals
- commitDays
- missionsCompleted
- missionsFirstTry

This tells us what topics the candidate knows.

-----------------------------------------

3. technical-spec.md

This defines the API.

We must expose
POST /api/interview

The interview should continue using
sessionId

The API should return
reply
done
feedback

==========================================
PROJECT REQUIREMENTS
==========================================

The interviewer must:

1. Read candidate profile
2. Read curriculum
3. Match completed curriculum days
4. Generate an interview plan
5. Ask one question at a time
6. Evaluate each answer
7. Decide:
   - Follow-up question OR Next topic
8. Continue until interview completes
9. Generate structured feedback

The interview should NOT be a fixed questionnaire.
It should adapt to the candidate's answers.

==========================================
ARCHITECTURE
==========================================

I want a modular architecture.

Example:
backend/
  api/
  services/
  models/
  prompts/
  memory/
  utils/

frontend/

Please recommend the best architecture.

==========================================
INTERVIEW FLOW
==========================================

Step 1: Frontend selects candidate.
↓
Step 2: Backend loads candidate profile.
↓
Step 3: Backend loads curriculum.
↓
Step 4: Generate interview plan.

Example:
Question 1: Embeddings
Question 2: Vector Databases
Question 3: Retrieval
Question 4: Prompt Engineering
Question 5: Backend
Question 6: Agents
Question 7: MCP
Question 8: Deployment

The interview plan should depend on the candidate profile.

==========================================
QUESTION GENERATION
==========================================

The AI should generate the interview questions.
The first question should NOT be hardcoded.

Instead:
Our code selects the topic while the LLM generates the wording.

Example:
Topic: Embeddings
LLM generates: "Can you explain how embeddings work and why they are useful in semantic search?"

If the candidate is senior, questions should become more difficult.
If junior, questions should be simpler.

==========================================
FOLLOW-UP QUESTIONS
==========================================

The AI should analyze every answer.

Example:
Question: Explain embeddings.
Candidate: Embeddings convert text into vectors.
AI: Good. You mentioned vectors. How is cosine similarity used during retrieval?

If the answer is weak: AI should ask "Can you elaborate?"
If answer is strong: Move to next topic.

==========================================
SCORING
==========================================

Every answer should receive:
- Correctness
- Depth
- Communication
- Confidence

Store the score.

==========================================
MEMORY
==========================================

Store:
- candidate
- conversation history
- current question
- scores
- interview plan

using sessionId.

The frontend should only send sessionId and message.
The backend should restore memory.

==========================================
FINAL REPORT
==========================================

Generate:
- Summary
- Strengths
- Weaknesses
- Recommendations
- Overall score
- Hiring readiness

==========================================
TECH STACK
==========================================

Use:
- Python
- FastAPI
- Pydantic
- OpenAI SDK / Async LLM SDK
- React
- TailwindCSS
- TypeScript

==========================================
WHAT I WANT FROM YOU
==========================================

I do NOT want all the code at once.
I want to build this incrementally.

Always follow this process:
1. Explain the current step.
2. Explain why we need it.
3. Explain how it fits into the whole architecture.
4. Write production-quality code.
5. Explain every important function.
6. Wait for me before moving to the next step.

==========================================
CODING STANDARDS
==========================================

Use:
- SOLID principles
- Clean architecture
- Dependency injection
- Type hints
- Pydantic models
- Modular services
- Well-structured prompts
- Proper error handling

==========================================
LLM PROMPTS
==========================================

Help me design:
- System prompts
- Evaluation prompts
- Follow-up prompts
- Final feedback prompts

==========================================
IMPORTANT
==========================================

Never jump ahead.
Always build the project one module at a time.
Act like my senior engineer and guide me through the entire project until it is complete.

##Prompt to Gemini

Prompt 1:
Review `client.py` for Python default argument issues and module loading bugs.

Prompt 2:
Should `curriculum.json` and `candidates.json` be moved inside the `backend/` directory for cleaner path resolution?

Prompt 3:
Refactor `GeminiLLMClient` to look up settings dynamically at instantiation rather than module load time.

Prompt 4:
Switch the backend from Gemini to Groq API using `AsyncGroq`.

Prompt 5:
Provide the updated `client.py` using `AsyncGroq` with support for JSON mode and standard completion.

Prompt 6:
Provide the updated `main.py` entrypoint configured to load `GroqLLMClient` dynamically from environment variables.

Prompt 7:
Ensure `GROQ_API_KEY` is loaded securely via `pydantic-settings` from `.env` without hardcoded strings.

Prompt 8:
Update `config.py` to declare `groq_api_key` alongside existing model settings.

Prompt 9:
Verify if the AI generated interview questions correctly based on the candidate's studied curriculum missions and completed topics.

Prompt 10:
Check the generated feedback summary, strengths, gaps, and next steps against the submission technical specification.

Prompt 11:
How do I test the `/health` endpoint locally using cURL, browser, and Swagger UI?
