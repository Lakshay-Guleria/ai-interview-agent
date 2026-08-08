// Mirrors backend/models/api_schemas.py and models/candidate.py.
// TODO (Codex): keep in sync manually, or generate from OpenAPI schema
// (FastAPI exposes /openapi.json — consider openapi-typescript for this).

export interface Mission {
  day: number;
  title: string;
  passed?: boolean;
  skipped?: boolean;
  attempts?: number;
}

export interface CandidateSignals {
  commitDays: number;
  missionsCompleted: number;
  missionsFirstTry: number;
}

export interface CandidateMember {
  id: string;
  name: string;
  jobRole: string;
  yearsExperience: number;
  education: string;
  status: string;
}

export interface Candidate {
  member: CandidateMember;
  missions: Mission[];
  signals: CandidateSignals;
}

export interface Feedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

export interface InterviewRequest {
  sessionId: string;
  candidate?: Candidate;
  message?: string;
}

export interface InterviewResponse {
  reply: string;
  done: boolean;
  feedback?: Feedback;
}
