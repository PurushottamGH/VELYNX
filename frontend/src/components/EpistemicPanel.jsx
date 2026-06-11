import React from 'react';

export default function EpistemicPanel({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return <div className="text-[11px] text-zinc-600 font-mono">// EPISTEMIC_FILTER: POLARIZING_MATRIX_OFFLINE</div>;
  }
  return (
    <div className="font-mono">
      <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">[02 // EPISTEMIC_HONESTY_REGISTER]</div>
      <div className="space-y-1">
        {Object.entries(data).map(([concept, status]) => {
          const isVerified = status === 'VERIFIED';
          const isUncertain = status === 'UNCERTAIN' || status === 'INFERRED';
          return (
            <div key={concept} className="flex justify-between items-center text-xs bg-zinc-950 p-2 border border-zinc-900">
              <span className="text-zinc-400">{concept.toLowerCase()}</span>
              <span className={`px-1 text-[10px] font-bold font-mono tracking-wide ${
                isVerified ? 'bg-zinc-800 text-zinc-200 border border-zinc-700' :
                isUncertain ? 'bg-amber-950/50 text-amber-500 border border-amber-900/50' : 'bg-zinc-900 text-zinc-500'
              }`}>
                {status}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}