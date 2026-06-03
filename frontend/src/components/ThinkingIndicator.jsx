export default function ThinkingIndicator({ monologueSteps, pipelineStage }) {
  if (!pipelineStage && monologueSteps.length === 0) return null;

  const isActive = pipelineStage?.status === 'active';

  return (
    <div className="rounded-xl border border-black/10 bg-white/50 p-4">
      <div className="flex items-center gap-2 mb-2">
        {isActive && (
          <span className="inline-block h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
        )}
        <h4 className="text-sm font-semibold text-black/70">
          VELYNX is thinking
          {pipelineStage?.stage && ` — ${pipelineStage.stage}`}
        </h4>
      </div>
      {monologueSteps.length > 0 && (
        <div className="space-y-1 mt-2">
          {monologueSteps.map((step, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-black/50">
              <span className="rounded bg-black/5 px-1.5 py-0.5 font-mono uppercase shrink-0">
                {step.type}
              </span>
              <span>{step.content}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
