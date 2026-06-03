export default function AccuracyDash({ confidence, sources = [] }) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white/70 p-5">
      <h3 className="text-lg font-semibold">Accuracy</h3>
      <div className="mt-3 space-y-2 text-sm text-black/70">
        <p>
          Confidence tier: <span className="font-semibold text-black">{confidence || 'UNKNOWN'}</span>
        </p>
        <p>
          Sources used: <span className="font-semibold text-black">{sources.length}</span>
        </p>
      </div>
    </div>
  );
}
