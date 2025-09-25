import clsx from "clsx";

export default function Card({ title, children, className = "", sectionClassName = "" }) {
  return (
    <section className={clsx("py-6", sectionClassName)}>
      <div className={clsx("card", className)}>
        {title && <h2 className="mb-4 text-center text-lg font-bold text-slate-800">{title}</h2>}
        {children}
      </div>
    </section>
  );
}
