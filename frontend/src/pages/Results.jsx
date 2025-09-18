import Card from '../components/Card'
import Gauge from '../components/Gauge'
import Button from '../components/Button'
import { useResult } from '../state/ResultContext'
import { Link, useNavigate } from 'react-router-dom'

export default function Results() {
  const { result } = useResult()
  const nav = useNavigate()
  if (!result)
    return (
      <Card title="No result">
        <p>Please run the calculator first.</p>
      </Card>
    )

  return (
    <Card title="Your Estimated Heart Disease Risk">
      <div className="grid gap-6 md:grid-cols-3">
        <div className="flex flex-col items-center">
          <Gauge value={result.risk_probability} />
          <p className="mt-2 text-sm text-slate-600">Probability</p>
          <p className="font-bold">{result.risk_level}</p>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h3 className="mb-3 font-bold text-slate-800">What affected your result</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            <li>Systolic blood pressure</li>
            <li>Cholesterol profile (Total/HDL/optional LDL)</li>
            <li>Smoking / Diabetes</li>
            <li>Medication status</li>
          </ul>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h3 className="mb-3 font-bold text-slate-800">How to lower your risk</h3>
          <ul className="space-y-2 text-sm text-slate-700">
            <li>Healthy eating pattern</li>
            <li>Regular physical activity</li>
            <li>Maintain a healthy weight</li>
            <li>Limit alcohol and avoid smoking</li>
          </ul>
          <Link to="/resources" className="mt-2 inline-block text-sm underline">
            See trusted resources
          </Link>
        </div>
      </div>

      <div className="mt-8 flex justify-center gap-3">
        <Button onClick={() => nav('/calculator')}>Re-take Assessment</Button>
        <Button className="bg-navy">Save Result</Button>
        <Button className="bg-slate-700">Download PDF</Button>
      </div>

      <p className="mt-6 text-center text-xs text-slate-500">
        No personal identifiers stored. This tool is for educational information and is not a
        medical diagnosis.
      </p>
    </Card>
  )
}
