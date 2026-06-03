"""SSE streaming client for VELYNX queries."""

export function streamQuery(text, sessionId, onEvent) {
  const params = new URLSearchParams({ text });
  if (sessionId) params.set('session_id', sessionId);

  const url = `http://localhost:8000/stream/query?${params.toString()}`;
  const eventSource = new EventSource(url);

  const handlers = {
    pipeline_stage: [],
    monologue_step: [],
    answer: [],
    stream_complete: [],
    error: [],
  };

  const dispatch = (type, data) => {
    if (handlers[type]) {
      handlers[type].forEach(fn => fn(data));
    }
    if (onEvent) onEvent(type, data);
  };

  const eventTypes = ['pipeline_stage', 'monologue_step', 'answer', 'stream_complete', 'error'];
  eventTypes.forEach(type => {
    eventSource.addEventListener(type, (e) => {
      try {
        const data = JSON.parse(e.data);
        dispatch(type, data);
      } catch {
        dispatch(type, { raw: e.data });
      }
    });
  });

  eventSource.onerror = () => {
    dispatch('error', { message: 'Connection lost' });
    eventSource.close();
  };

  // Auto-close on stream_complete
  const origComplete = handlers.stream_complete;
  handlers.stream_complete = [(data) => {
    eventSource.close();
    origComplete.forEach(fn => fn(data));
  }];

  return {
    eventSource,
    on(type, fn) {
      if (handlers[type]) handlers[type].push(fn);
      return this;
    },
    close() {
      eventSource.close();
    },
  };
}
