import clsx from "clsx";

export default function Segment({ name, setValue, options, defaultIndex = 0 }) {
  return (
    <div className="inline-flex overflow-hidden rounded-md border border-slate-300 bg-slate-200">
      {options.map(([val, label], idx) => (
        <button
          key={val}
          type="button"
          className={clsx("px-4 py-2 text-sm font-semibold text-slate-700", idx === defaultIndex && "bg-navy text-white")}
          onClick={(e) => {
            const parent = e.currentTarget.parentElement;
            [...parent.children].forEach((btn) => btn.classList.remove("bg-navy", "text-white"));
            e.currentTarget.classList.add("bg-navy", "text-white");
            setValue(name, val, { shouldValidate: true, shouldDirty: true });
          }}>
          {label}
        </button>
      ))}
    </div>
  );
}
