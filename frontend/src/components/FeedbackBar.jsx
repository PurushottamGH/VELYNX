import { useMemo, useState } from 'react';
import { postFeedback } from '../api/velynx.js';

const FEEDBACK_TYPES = [
  { key: 'accurate', label: 'Accurate', rating: 1 },
  { key: 'wrong', label: 'Wrong', rating: -1 },
  { key: 'incomplete', label: 'Incomplete', rating: 0 },
];

export default function FeedbackBar({
  answerId,
  queryText,
  answer,
  confidence,
  sources = [],
  contradictions = [],
  gaps = [],
  debug,
}) {
  const [activeType, setActiveType] = useState(null);
  const [correction, setCorrection] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const canSend = Boolean(queryText && answer);
  const isWrong = activeType === 'wrong';

  const payloadBase = useMemo(() => {
    const safeSources = (sources || []).filter((item) => item?.source);
    const sourceDomains = [...new Set(safeSources.map((item) => item.source).filter(Boolean))];
    return {
      query: queryText,
      meta: {
        answerId: answerId || null,
        queryText,
        answer,
        confidence,
        source_count: safeSources.length,
        source_domains: sourceDomains,
        contradiction_count: contradictions.length,
        gap_count: gaps.length,
        contradictions,
        gaps,
        strategy: debug?.intent?.strategy,
        weights: debug?.intent?.weights,
        sources: safeSources.map((item) => ({
          source: item.source,
          url: item.url,
          score: item.score,
        })),
      },
    };
  }, [answer, answerId, confidence, contradictions, debug, gaps, queryText, sources]);

  const handleFeedback = async (type) => {
    const selected = FEEDBACK_TYPES.find((item) => item.key === type);
    if (!selected || !canSend || isLoading) return;

    setActiveType(type);
    setIsLoading(true);
    setStatus(null);
    setError(null);

    try {
      const payload = {
        ...payloadBase,
        rating: selected.rating,
        type: selected.key,
        correction: isWrong ? correction.trim() || undefined : undefined,
      };
      await postFeedback(payload);
      setStatus('VELYNX learned from this.');
      if (type !== 'wrong') {
        setCorrection('');
      }
    } catch (err) {
      setError('Could not save feedback. Try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-4 rounded-2xl border border-white/10 bg-black/70 p-4 text-white shadow-lg">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-white/70">Feedback</p>
        <div className="flex flex-wrap gap-2">
          {FEEDBACK_TYPES.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => handleFeedback(item.key)}
              disabled={!canSend || isLoading}
              className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide transition ${
                activeType === item.key
                  ? 'border-white bg-white text-black'
                  : 'border-white/40 bg-white/10 text-white hover:bg-white/20'
              } disabled:cursor-not-allowed disabled:opacity-50`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {isWrong ? (
        <div className="mt-3">
          <label className="text-xs font-semibold uppercase tracking-wide text-white/70">
            Correction (optional)
          </label>
          <textarea
            value={correction}
            onChange={(event) => setCorrection(event.target.value)}
            rows={2}
            className="mt-2 w-full rounded-lg border border-white/10 bg-black/60 px-3 py-2 text-sm text-white placeholder:text-white/40 focus:border-white/40 focus:outline-none"
            placeholder="What should VELYNX learn instead?"
          />
        </div>
      ) : null}

      <div className="mt-3 flex items-center justify-between text-xs">
        {isLoading ? <span className="text-white/70">Saving feedback...</span> : null}
        {!isLoading && status ? <span className="text-emerald-300">{status}</span> : null}
        {!isLoading && error ? <span className="text-red-300">{error}</span> : null}
      </div>
    </div>
  );
}
