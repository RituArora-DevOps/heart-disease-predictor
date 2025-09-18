import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Optional interceptors → show toasts on error (hooked by components/Toast.jsx)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    window.dispatchEvent(
      new CustomEvent('toast', { detail: { type: 'error', msg: apiErrorMsg(err) } })
    )
    return Promise.reject(err)
  }
)

function apiErrorMsg(err) {
  if (err.response?.status === 422) return 'Validation error: please check your inputs.'
  if (err.code === 'ECONNABORTED') return 'Request timed out. Try again.'
  if (err.response?.status >= 500) return 'Server error. Please try again later.'
  return 'Network error. Please check your connection.'
}

export async function postPredict(payload) {
  const { data } = await api.post('/predict', payload)
  return data // { risk_probability: number, risk_level: 'Low'|'Medium'|'High' }
}
