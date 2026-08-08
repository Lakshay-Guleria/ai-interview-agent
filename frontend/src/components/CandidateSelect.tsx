import type { Candidate } from "../types/api";

interface Props {
  candidates: Candidate[];
  selectedId: string | null;
  onSelect: (candidate: Candidate) => void;
}

function completionRate(candidate: Candidate) {
  const total = candidate.missions.length || 1;
  const passed = candidate.missions.filter((mission) => mission.passed).length;
  return Math.round((passed / total) * 100);
}

export default function CandidateSelect({ candidates, selectedId, onSelect }: Props) {
  return (
    <aside className="border-r border-zinc-200 bg-zinc-50">
      <div className="sticky top-0 z-10 border-b border-zinc-200 bg-zinc-50 px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Candidates</p>
        <h1 className="mt-1 text-xl font-semibold text-zinc-950">AI Interview Agent</h1>
      </div>

      <div className="flex flex-col gap-2 p-3">
        {candidates.map((candidate) => {
          const isSelected = candidate.member.id === selectedId;
          return (
            <button
              key={candidate.member.id}
              onClick={() => onSelect(candidate)}
              className={`rounded-md border px-4 py-3 text-left transition ${
                isSelected
                  ? "border-zinc-950 bg-white shadow-sm"
                  : "border-transparent bg-transparent hover:border-zinc-200 hover:bg-white"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-zinc-950">{candidate.member.name}</p>
                  <p className="mt-1 text-sm text-zinc-600">{candidate.member.jobRole}</p>
                </div>
                <span className="shrink-0 rounded bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800">
                  {completionRate(candidate)}%
                </span>
              </div>
              <div className="mt-3 flex gap-3 text-xs text-zinc-500">
                <span>{candidate.member.yearsExperience} yrs</span>
                <span>{candidate.signals.missionsFirstTry} first try</span>
                <span>{candidate.signals.commitDays} commits</span>
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
