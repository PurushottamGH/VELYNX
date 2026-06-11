import React from 'react';
import { useChatStore } from '../store/velynx';
import ResonancePanel from './ResonancePanel';
import EpistemicPanel from './EpistemicPanel';
import MemoryPanel from './MemoryPanel';

export default function Pipeline() {
  const messages = useChatStore((state) => state.messages);
  
  // Automatically pull telemetry from the last generated assistant message
  const lastAssistantMessage = [...messages].reverse().find(m => m.role === 'assistant');
  const telemetry = lastAssistantMessage?.telemetry || null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 h-screen w-screen bg-black text-white font-mono p-4 gap-4 overflow-hidden select-none">
      {/* LEFT SECTION: Main Conversation Core */}
      <div className="lg:col-span-2 flex flex-col border border-zinc-800 bg-black h-full overflow-hidden">
        <div className="text-[10px] uppercase tracking-widest text-zinc-500 p-3 border-b border-zinc-800 flex justify-between items-center bg-zinc-950">
          <span>// PRIMARY_STREAM_CONVERGENCE</span>
          <span className="text-emerald-500 animate-pulse">● ONLINE</span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`p-3 border ${msg.role === 'user' ? 'border-zinc-800 bg-zinc-950/40 text-right' : 'border-zinc-800 bg-black'}`}>
              <div className="text-[9px] uppercase tracking-wider text-zinc-600 mb-1">
                [{msg.role === 'user' ? 'SRC_INPUT' : 'CORE_REPLY'}]
              </div>
              <p className="text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">{msg.content}</p>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT SECTION: Subconscious Telemetry Array */}
      <div className="flex flex-col border border-zinc-800 bg-zinc-950 h-full overflow-hidden divide-y divide-zinc-800">
        <div className="p-3 bg-black flex justify-between items-center">
          <span className="text-[10px] uppercase tracking-widest text-zinc-400 font-bold">SUBCONSCIOUS_STATE_DIAGNOSTIC</span>
          <span className="text-[9px] text-zinc-600">SYS_V1.0</span>
        </div>
        
        <div className="flex-1 p-3 overflow-y-auto bg-black">
          <ResonancePanel data={telemetry?.resonanceScores} />
        </div>
        
        <div className="flex-1 p-3 overflow-y-auto bg-black">
          <EpistemicPanel data={telemetry?.epistemicStates} />
        </div>
        
        <div className="flex-1 p-3 overflow-y-auto bg-black">
          <MemoryPanel data={telemetry?.recalledMemory} />
        </div>
      </div>
    </div>
  );
}