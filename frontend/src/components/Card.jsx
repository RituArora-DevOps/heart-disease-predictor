import clsx from "clsx";

export default function Card({ title, children, className = "", panelClassName = "", bodyClassName = "" }) {
  return (
    <section className={clsx("py-6", className)}>
      <div className={clsx("card rounded-2xl bg-slate-50 shadow-sm ring-1 ring-black/5 p-6", "mx-auto h-full", panelClassName)}>
        {title && <h2 className="mb-6 text-center text-xl font-bold text-slate-800">{title}</h2>}
        <div className={clsx("h-full", bodyClassName)}>{children}</div>
      </div>
    </section>
  );
}
