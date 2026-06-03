export default function SearchBar({ value, onChange, onSubmit, isLoading }) {
  return (
    <form
      onSubmit={onSubmit}
      className="rounded-2xl border border-black/10 bg-white/70 px-4 py-3 shadow-sm backdrop-blur"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          className="w-full bg-transparent text-lg outline-none"
          placeholder="Ask VELYNX a question..."
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <button
          type="submit"
          disabled={isLoading || !value.trim()}
          className="rounded-full bg-black px-5 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-black/40"
        >
          {isLoading ? 'Thinking...' : 'Run'}
        </button>
      </div>
    </form>
  );
}
