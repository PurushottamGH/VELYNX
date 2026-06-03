import FeedbackBar from './FeedbackBar.jsx';

export default function Answer({
  answer,
  confidence,
  queryText,
  answerId,
  sources,
  contradictions,
  gaps,
  debug,
  isStreaming,
  partialAnswer,
}) {
  const displayAnswer = isStreaming ? partialAnswer : answer;

  return (
    <div className="rounded-2xl border border-black/10 bg-white/70 p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Answer</h3>
        <span className="rounded-full bg-black/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
          {confidence || 'UNKNOWN'}
        </span>
      </div>
      <p className="mt-3 text-sm text-black/70">
        {displayAnswer || 'Submit a query to see VELYNX respond with sources and confidence.'}
        {isStreaming && <span className="inline-block w-1.5 h-4 bg-black/40 ml-0.5 animate-pulse" />}
      </p>
      {!isStreaming && answer && (
        <FeedbackBar
          answerId={answerId}
          queryText={queryText}
          answer={answer}
          confidence={confidence}
          sources={sources}
          contradictions={contradictions}
          gaps={gaps}
          debug={debug}
        />
      )}
    </div>
  );
}
