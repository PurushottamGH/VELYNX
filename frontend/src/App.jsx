import { motion } from 'framer-motion';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import SearchBar from './components/SearchBar.jsx';
import Pipeline from './components/Pipeline.jsx';
import Answer from './components/Answer.jsx';
import Sources from './components/Sources.jsx';
import Analysis from './components/Analysis.jsx';
import AccuracyDash from './components/AccuracyDash.jsx';
import ThinkingIndicator from './components/ThinkingIndicator.jsx';
import { getHealth, postQuery } from './api/velynx.js';
import useStreamingQuery from './hooks/useStreamingQuery.js';

export default function App() {
  const [queryText, setQueryText] = useState('');
  const [lastSubmittedQuery, setLastSubmittedQuery] = useState('');
  const { data } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
  });
  const queryMutation = useMutation({
    mutationFn: postQuery,
  });
  const { answer: streamAnswer, isStreaming, pipelineStage, monologueSteps, error: streamError, startQuery } = useStreamingQuery();

  // Use streaming answer if available, fall back to mutation
  const response = streamAnswer || queryMutation.data;
  const isActive = isStreaming || queryMutation.isPending || Boolean(response);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!queryText.trim()) return;
    const normalized = queryText.trim();
    setLastSubmittedQuery(normalized);
    // Try streaming first
    startQuery(normalized);
  };

  const answerId =
    response?.debug?.memory?.episode_id ||
    response?.debug?.intent?.query ||
    response?.query ||
    lastSubmittedQuery ||
    null;

  return (
    <main className="relative min-h-screen bg-gradient-to-b from-[#f7f2ea] via-[#f1e7d7] to-[#efe1c9] text-[#1b1b1b]">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-10 top-10 h-48 w-48 rounded-full bg-[#ffb37b]/40 blur-3xl" />
        <div className="absolute right-16 top-32 h-64 w-64 rounded-full bg-[#7bd3ff]/35 blur-3xl" />
        <div className="absolute bottom-10 left-1/3 h-56 w-56 rounded-full bg-[#ffd36a]/40 blur-3xl" />
      </div>

      <header className="relative mx-auto max-w-6xl px-6 pt-16">
        <motion.p
          className="font-mono text-xs uppercase tracking-[0.3em] text-[#5a4b3a]"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          The Raised Mind
        </motion.p>
        <motion.h1
          className="mt-4 text-5xl font-semibold tracking-tight sm:text-6xl"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          VELYNX
        </motion.h1>
        <motion.p
          className="mt-4 max-w-2xl text-lg text-[#3f352b]"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          A pipeline-aware search mind that explains sources, contradictions, and confidence.
        </motion.p>
        <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <SearchBar
            value={queryText}
            onChange={setQueryText}
            onSubmit={handleSubmit}
            isLoading={isStreaming}
          />
          <div className="rounded-2xl border border-black/10 bg-white/70 p-4 text-sm">
            <p className="font-semibold">Backend status</p>
            <p className="mt-2 text-black/70">
              {data?.status ? `API: ${data.status}` : 'Waiting for API...'}
            </p>
            {queryMutation.isError || streamError ? (
              <p className="mt-2 text-xs text-red-700">{streamError || 'Query failed. Try again.'}</p>
            ) : null}
          </div>
        </div>
      </header>

      <section className="relative mx-auto mt-14 max-w-6xl px-6">
        <motion.h2
          className="text-xl font-semibold"
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
        >
          Live Pipeline
        </motion.h2>
        <p className="mt-2 text-sm text-black/60">
          Each layer activates as VELYNX reasons across sources.
        </p>
        <div className="mt-6">
          <Pipeline isActive={isActive} activeStage={pipelineStage} />
        </div>
      </section>

      <section className="relative mx-auto mt-12 grid max-w-6xl gap-6 px-6 pb-16 lg:grid-cols-2">
        <ThinkingIndicator monologueSteps={monologueSteps} pipelineStage={pipelineStage} />
        <Answer
          answer={response?.answer}
          confidence={response?.confidence}
          queryText={lastSubmittedQuery}
          answerId={answerId}
          sources={response?.sources || []}
          contradictions={response?.contradictions || []}
          gaps={response?.gaps || []}
          debug={response?.debug}
          isStreaming={isStreaming}
          partialAnswer={streamAnswer?.answer}
        />
        <AccuracyDash confidence={response?.confidence} sources={response?.sources || []} />
        <Sources sources={response?.sources || []} />
        <Analysis contradictions={response?.contradictions || []} />
      </section>
    </main>
  );
}
