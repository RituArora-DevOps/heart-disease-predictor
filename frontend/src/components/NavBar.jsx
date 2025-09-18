import { NavLink } from 'react-router-dom'

const link = ({ isActive }) =>
  [
    'px-5 text-lg font-semibold transition-colors',
    isActive ? 'text-white' : 'text-slate-400 hover:text-white',
  ].join(' ')

export default function NavBar() {
  return (
    <header className="bg-navy">
      <nav className="container flex items-center justify-between py-5">
        <div className="text-3xl font-extrabold tracking-wide">CardioRisk</div>
        <div className="flex gap-6">
          <NavLink to="/" end className={link}>
            Home
          </NavLink>
          <NavLink to="/calculator" className={link}>
            Calculator
          </NavLink>
          <NavLink to="/resources" className={link}>
            Resources
          </NavLink>
          <NavLink to="/disclaimer" className={link}>
            Disclaimer
          </NavLink>
        </div>
      </nav>
    </header>
  )
}
