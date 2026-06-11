import React from 'react';

export default function ResonancePanel({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return <div className="text-[11px] text-zinc-600 font-mono">// RESONANCE_WAVE: IDLE_WAITING_FOR_IMPULSE</div>;
  }
  return (
    <div className="font-mono">
      <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">[01 // RESONANCE_WAVE_PROPAGATION]</div>
      <div className="space-y-1">
        {Object.entries(data).map(([concept, score]) => (
          <div key={concept} className="flex justify-between items-center text-xs bg-zinc-950 p-2 border border-zinc-900">
            <span className="text-zinc-400 tracking-tight">{concept.toUpperCase()}</span>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] text-zinc-600">{(score * 100).toFixed(0)}%</span>
              <span className="text-emerald-500 font-bold tracking-tighter">{(score).toFixed(4)}Hz</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}