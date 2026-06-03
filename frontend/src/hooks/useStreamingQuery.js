import { useState, useCallback, useRef } from 'react';
import { streamQuery } from '../api/streaming.js';

export default function useStreamingQuery() {
  const [answer, setAnswer] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [pipelineStage, setPipelineStage] = useState(null);
  const [monologueSteps, setMonologueSteps] = useState([]);
  const [error, setError] = useState(null);
  const streamRef = useRef(null);

  const startQuery = useCallback((text, sessionId) => {
    // Reset state
    setAnswer(null);
    setIsStreaming(true);
    setPipelineStage(null);
    setMonologueSteps([]);
    setError(null);

    const stream = streamQuery(text, sessionId, (type, data) => {
      switch (type) {
        case 'pipeline_stage':
          setPipelineStage(data);
          break;
        case 'monologue_step':
          setMonologueSteps(prev => [...prev, data]);
          break;
        case 'answer':
          setAnswer(data);
          setIsStreaming(false);
          break;
        case 'error':
          setError(data.message || 'Stream error');
          setIsStreaming(false);
          break;
        case 'stream_complete':
          setIsStreaming(false);
          break;
      }
    });

    streamRef.current = stream;
    return stream;
  }, []);

  const cancel = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  return {
    answer,
    isStreaming,
    pipelineStage,
    monologueSteps,
    error,
    startQuery,
    cancel,
  };
}
