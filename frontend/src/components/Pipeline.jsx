const STEPS = ['Context', 'Dialogue', 'Intent', 'Retrieval', 'Truth', 'Contradiction', 'Monologue', 'Reasoning', 'Synthesis', 'Reflection'];

const STAGE_MAP = {
  context: 'Context',
  dialogue: 'Dialogue',
  intent: 'Intent',
  retrieval: 'Retrieval',
  truth: 'Truth',
  contradiction: 'Contradiction',
  monologue: 'Monologue',
  reasoning: 'Reasoning',
  reasoning_mode: 'Reasoning',
  synthesis: 'Synthesis',
  reflection: 'Reflection',
};

export default function Pipeline({ isActive, activeStage }) {
  const currentStageName = activeStage?.stage ? STAGE_MAP[activeStage.stage] : null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {STEPS.map((step) => {
        const isCurrent = isActive && currentStageName === step && activeStage?.status === 'active';
        const isCompleted = isActive && currentStageName && STEPS.indexOf(step) < STEPS.indexOf(currentStageName);
        return (
          <div
            key={step}
            className={`rounded-xl border border-black/10 px-4 py-3 text-sm transition ${
              isCurrent
                ? 'bg-black/85 text-white animate-pulse'
                : isCompleted || (isActive && !currentStageName)
                  ? 'bg-black/85 text-white'
                  : 'bg-white/70'
            }`}
          >
            {step}
          </div>
        );
      })}
    </div>
  );
}
