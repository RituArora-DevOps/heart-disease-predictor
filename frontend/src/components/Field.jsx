export default function Field({ label, unit, error, children }) {
  return (
    <div>
      <label className="text-sm font-semibold text-slate-800">
        {label}
        {unit && <span className="ml-1 text-xs text-slate-500">({unit})</span>}
      </label>
      <div className="mt-1">{children}</div>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
