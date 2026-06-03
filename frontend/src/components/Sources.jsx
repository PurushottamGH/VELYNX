export default function Sources({ sources = [] }) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white/70 p-5">
      <h3 className="text-lg font-semibold">Sources</h3>
      {sources.length === 0 ? (
        <p className="mt-2 text-sm text-black/70">No sources yet.</p>
      ) : (
        <ul className="mt-4 space-y-3 text-sm text-black/70">
          {sources.map((source) => (
            <li key={source.url} className="rounded-xl border border-black/10 bg-white/60 p-3">
              <p className="font-semibold text-black">{source.title || source.url}</p>
              <p className="mt-1 text-xs uppercase tracking-wide">{source.source || 'source'}</p>
              <p className="mt-1 text-xs">Score: {source.score ?? 'n/a'}</p>
              <a className="mt-2 inline-block text-xs underline" href={source.url} target="_blank" rel="noreferrer">
                Open source
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
