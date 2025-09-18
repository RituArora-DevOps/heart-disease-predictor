import { useEffect, useState } from 'react'
export default function Toast() {
  const [msg, setMsg] = useState(null)
  useEffect(() => {
    const on = (e) => {
      setMsg(e.detail)
      setTimeout(() => setMsg(null), 3000)
    }
    window.addEventListener('toast', on)
    return () => window.removeEventListener('toast', on)
  }, [])
  if (!msg) return null
  const color = msg.type === 'error' ? 'bg-red-600' : 'bg-emerald-600'
  return (
    <div
      className={`fixed bottom-5 left-1/2 -translate-x-1/2 ${color} rounded px-4 py-2 text-white`}
    >
      {msg.msg}
    </div>
  )
}
