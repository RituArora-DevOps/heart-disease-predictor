export default function Card({ title, children }) {
  return (
    <section className="py-6">
      <div className="card">
        {title && <h2 className="mb-4 text-center text-lg font-bold text-slate-800">{title}</h2>}
        {children}
      </div>
    </section>
  )
}
