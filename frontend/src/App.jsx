import { Routes, Route } from 'react-router-dom'
import routes from './routes'
import NavBar from './components/NavBar'
import ErrorBoundary from './components/ErrorBoundary'
import { ResultProvider } from './state/ResultContext'
import Toast from './components/Toast'

export default function App() {
  return (
    <ResultProvider>
      <NavBar />
      <main className="container py-4">
        <ErrorBoundary>
          <Routes>
            {routes.map((r) => (
              <Route key={r.path} path={r.path} element={<r.element />} />
            ))}
          </Routes>
        </ErrorBoundary>
      </main>
      <Toast />
    </ResultProvider>
  )
}
