export default function Analysis({ contradictions = [] }) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white/70 p-5">
      <h3 className="text-lg font-semibold">Analysis</h3>
      {contradictions.length === 0 ? (
        <p className="mt-2 text-sm text-black/70">No contradictions detected.</p>
      ) : (
        <ul className="mt-3 space-y-2 text-sm text-black/70">
          {contradictions.map((item, index) => (
            <li key={index} className="rounded-lg border border-black/10 bg-white/60 p-2">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
