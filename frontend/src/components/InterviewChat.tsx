import { useState } from "react";
import { sendInterviewTurn } from "../lib/api";
import type { Candidate, Feedback } from "../types/api";

interface ChatMessage {
  role: "interviewer" | "candidate";
  content: string;
}

interface Props {
  sessionId: string;
  candidate: Candidate;
}

export default function InterviewChat({ sessionId, candidate }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [done, setDone] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startInterview() {
    setLoading(true);
    setError(null);
    try {
      const res = await sendInterviewTurn({ sessionId, candidate });
      setMessages([{ role: "interviewer", content: res.reply }]);
      setStarted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start interview.");
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = { role: "candidate", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const res = await sendInterviewTurn({ sessionId, message: userMsg.content });
      setMessages((prev) => [...prev, { role: "interviewer", content: res.reply }]);
      if (res.done) {
        setDone(true);
        setFeedback(res.feedback ?? null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send answer.");
    } finally {
      setLoading(false);
    }
  }

  if (!started) {
    return (
      <section className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-10">
        <div className="max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">Selected candidate</p>
          <h2 className="mt-2 text-3xl font-semibold text-zinc-950">{candidate.member.name}</h2>
          <p className="mt-2 text-zinc-600">
            {candidate.member.jobRole} / {candidate.member.yearsExperience} years / {candidate.member.education}
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-md border border-zinc-200 p-4">
              <p className="text-2xl font-semibold">{candidate.signals.missionsCompleted}</p>
              <p className="mt-1 text-sm text-zinc-500">missions completed</p>
            </div>
            <div className="rounded-md border border-zinc-200 p-4">
              <p className="text-2xl font-semibold">{candidate.signals.missionsFirstTry}</p>
              <p className="mt-1 text-sm text-zinc-500">first try passes</p>
            </div>
            <div className="rounded-md border border-zinc-200 p-4">
              <p className="text-2xl font-semibold">{candidate.signals.commitDays}</p>
              <p className="mt-1 text-sm text-zinc-500">commit days</p>
            </div>
          </div>

          {error && <p className="mt-5 rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</p>}

          <button
            className="mt-8 rounded-md bg-zinc-950 px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            onClick={startInterview}
            disabled={loading}
          >
            {loading ? "Starting interview..." : "Start interview"}
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="flex min-h-screen flex-col">
      <header className="border-b border-zinc-200 px-6 py-4">
        <p className="text-sm text-zinc-500">Interviewing</p>
        <h2 className="text-xl font-semibold">{candidate.member.name}</h2>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-3">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[82%] rounded-md px-4 py-3 text-sm leading-6 ${
                m.role === "interviewer" ? "self-start bg-zinc-100 text-zinc-950" : "self-end bg-zinc-950 text-white"
              }`}
            >
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="self-start rounded-md bg-zinc-100 px-4 py-3 text-sm text-zinc-500">Thinking...</div>
          )}
        </div>
      </div>

      <div className="border-t border-zinc-200 px-6 py-4">
        <div className="mx-auto max-w-3xl">
          {error && <p className="mb-3 rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</p>}

          {!done && (
            <div className="flex gap-2">
              <input
                className="min-w-0 flex-1 rounded-md border border-zinc-300 px-3 py-3 outline-none focus:border-zinc-950"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Type your answer..."
                disabled={loading}
              />
              <button
                className="rounded-md bg-zinc-950 px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                onClick={sendMessage}
                disabled={loading || !input.trim()}
              >
                Send
              </button>
            </div>
          )}

          {done && feedback && (
            <div className="rounded-md border border-zinc-200 p-5">
              <h2 className="text-lg font-semibold">Interview feedback</h2>
              <p className="mt-2 text-sm leading-6 text-zinc-700">{feedback.summary}</p>
              <div className="mt-5 grid gap-5 md:grid-cols-3">
                <div>
                  <strong className="text-sm">Strengths</strong>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-700">
                    {feedback.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong className="text-sm">Gaps</strong>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-700">
                    {feedback.gaps.map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong className="text-sm">Next steps</strong>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-700">
                    {feedback.next.map((n, i) => (
                      <li key={i}>{n}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
