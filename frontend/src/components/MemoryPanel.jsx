import React from 'react';

export default function MemoryPanel({ data }) {
  if (!data) {
    return <div className="text-[11px] text-zinc-600 font-mono">// EPISODIC_RECALL: VEC_STORE_NULL_RETURN</div>;
  }
  return (
    <div className="font-mono text-xs">
      <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2">[03 // VECTOR_GRAPH_RECALL_SNAPSHOT]</div>
      <div className="bg-zinc-950 p-3 border border-zinc-900 space-y-2">
        <div className="flex justify-between items-center border-b border-zinc-900 pb-1 text-[10px]">
          <span className="text-zinc-500">TAG_ANCHOR:</span>
          <span className="text-blue-400 font-bold">#{data.concept}</span>
        </div>
        <div>
          <span className="text-[9px] uppercase tracking-wider text-zinc-600 block">HISTORIC_PROMPT</span>
          <p className="text-zinc-400 italic text-[11px] mt-0.5">"{data.prompt}"</p>
        </div>
        <div>
          <span className="text-[9px] uppercase tracking-wider text-zinc-600 block">COMPUTED_OUTCOME</span>
          <p className="text-zinc-300 text-[11px] mt-0.5">"{data.answer}"</p>
        </div>
      </div>
    </div>
  );
}