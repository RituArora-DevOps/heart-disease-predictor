// Map backend -> UI shape expected by Results.jsx
export async function postPredict(payload) {
  const { data } = await api.post("/predict", payload);

  const probability =
    data?.probability != null ? Number(data.probability)
    : data?.risk_probability != null ? Number(data.risk_probability)
    : 0;

  const threshold = data?.threshold_used != null ? Number(data.threshold_used) : 0.5;

  return {
    probability,
    threshold_used: threshold,
    prediction:
      data?.prediction != null ? Number(data.prediction)
      : probability >= threshold ? 1
      : 0,
    _raw: data,
  };
}
