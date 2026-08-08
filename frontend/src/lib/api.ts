import type { InterviewRequest, InterviewResponse } from "../types/api";
import type { Candidate } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchCandidates(): Promise<Candidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/candidates`);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Candidate API error (${res.status}): ${detail}`);
  }

  return res.json();
}

export async function sendInterviewTurn(request: InterviewRequest): Promise<InterviewResponse> {
  const res = await fetch(`${API_BASE_URL}/api/interview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Interview API error (${res.status}): ${detail}`);
  }

  return res.json();
}