import axios from "axios";

// const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    window.dispatchEvent(new CustomEvent("toast", { detail: { type: "error", msg: apiErrorMsg(err) } }));
    return Promise.reject(err);
  }
);

function apiErrorMsg(err) {
  if (err.response?.status === 422) return "Validation error: please check your inputs.";
  if (err.code === "ECONNABORTED") return "Request timed out. Try again.";
  if (err.response?.status >= 500) return "Server error. Please try again later.";
  return "Network error. Please check your connection.";
}

function normalizePredictResponse(raw) {
  let probability = raw?.probability;
  let prediction = raw?.prediction;
  let threshold_used = raw?.threshold_used;

  if (probability == null && raw?.risk_probability != null) {
    probability = raw.risk_probability;
  }
  if (prediction == null && raw?.risk_level) {
    prediction = raw.risk_level === "High" ? 1 : 0;
  }
  if (threshold_used == null) {
    threshold_used = raw?.threshold ?? 0.5;
  }

  return {
    probability: Number(probability ?? 0),
    prediction: Number(prediction ?? 0),
    threshold_used: Number(threshold_used ?? 0.5),
  };
}

export async function postPredict(payload) {
  const { data } = await api.post("/predict", payload);
  return normalizePredictResponse(data);
}
