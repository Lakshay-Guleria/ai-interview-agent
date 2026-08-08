import { useEffect, useState } from "react";
import CandidateSelect from "./components/CandidateSelect";
import InterviewChat from "./components/InterviewChat";
import { fetchCandidates } from "./lib/api";
import type { Candidate } from "./types/api";

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCandidates()
      .then((loaded) => {
        setCandidates(loaded);
        setSelectedCandidate(loaded[0] ?? null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function selectCandidate(candidate: Candidate) {
    setSelectedCandidate(candidate);
    setSessionId(crypto.randomUUID());
  }

  return (
    <div className="grid min-h-screen bg-white text-zinc-950 md:grid-cols-[360px_1fr]">
      <CandidateSelect
        candidates={candidates}
        selectedId={selectedCandidate?.member.id ?? null}
        onSelect={selectCandidate}
      />

      <main className="min-w-0">
        {loading && (
          <div className="flex min-h-screen items-center justify-center text-sm text-zinc-500">
            Loading candidates...
          </div>
        )}

        {error && (
          <div className="mx-auto mt-12 max-w-xl rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error}
          </div>
        )}

        {!loading && !error && selectedCandidate && (
          <InterviewChat key={sessionId} sessionId={sessionId} candidate={selectedCandidate} />
        )}
      </main>
    </div>
  );
}
