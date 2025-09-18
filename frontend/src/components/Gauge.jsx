export default function Gauge({ value = 0 }) {
  const pct = Math.max(0, Math.min(1, value))
  const angle = 180 * pct
  const r = 70,
    cx = 90,
    cy = 90
  const p = pol(cx, cy, r, 180),
    q = pol(cx, cy, r, 180 - angle)
  const d = `M ${p.x} ${p.y} A ${r} ${r} 0 ${angle > 180 ? 1 : 0} 1 ${q.x} ${q.y}`
  const color = pct < 0.33 ? '#16a34a' : pct < 0.66 ? '#f59e0b' : '#dc2626'
  return (
    <svg width="220" height="140" className="mx-auto">
      <path
        d={`M ${pol(cx, cy, r, 180).x} ${pol(cx, cy, r, 180).y} A ${r} ${r} 0 1 1 ${pol(cx, cy, r, 0).x} ${pol(cx, cy, r, 0).y}`}
        stroke="#e5e7eb"
        strokeWidth="12"
        fill="none"
      />
      <path d={d} stroke={color} strokeWidth="12" fill="none" />
      <text x={cx} y={cy} textAnchor="middle" fill="#0f172a" fontSize="20" fontWeight="800">
        {(pct * 100).toFixed(0)}%
      </text>
    </svg>
  )
}
function pol(cx, cy, r, deg) {
  const rad = (deg * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}
