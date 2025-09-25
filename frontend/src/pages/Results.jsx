import Card from "../components/Card";
import Gauge from "../components/Gauge";
import Button from "../components/Button";
import { useResult } from "../state/ResultContext";
import { Link, useNavigate } from "react-router-dom";

export default function Results() {
  const { result } = useResult();
  const nav = useNavigate();

  if (!result) {
    return (
      <Card title="No result">
        <p>Please run the calculator first.</p>
      </Card>
    );
  }

  // —— 计算与容错（在 return 之前，但不渲染 JSX）——
  const prob = Number(result?.probability ?? 0);
  const thr = Number(result?.threshold_used ?? 0.5);

  function riskLevel(p, t = 0.5) {
    if (!Number.isFinite(p)) return "—";
    if (p < 0.2) return "Low";
    if (p < t) return "Medium";
    return "High";
  }

  return (
    <Card title="Your Estimated Heart Disease Risk" className="min-h-[560px] p-10">
      <div className="flex h-full flex-col">
        {/* 两列：左侧仪表盘，右侧建议 */}
        <div className="mt-9 grid grid-cols-1 gap-16 md:grid-cols-2 max-w-[1050px] mx-auto">
          {/* 左：概率卡片 */}
          <div className="rounded-xl bg-white p-6 shadow-sm flex flex-col items-center">
            <Gauge value={prob} width={280} />
            <p className="mt-3 text-sm text-slate-600">Probability</p>
            <p className="font-bold">{riskLevel(prob, thr)}</p>
          </div>

          {/* 右：建议卡片 */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-bold text-slate-800">How to lower your risk</h3>
            <ul className="text-sm leading-relaxed space-y-2 text-slate-700">
              <li>Healthy eating pattern</li>
              <li>Regular physical activity</li>
              <li>Maintain a healthy weight</li>
              <li>Limit alcohol and avoid smoking</li>
            </ul>
            <Link to="/resources" className="mt-4 inline-block text-sm underline">
              See trusted resources
            </Link>
          </div>
        </div>

        {/* 按钮区与声明 */}
        <div className="mt-22 flex justify-center gap-3">
          <Button onClick={() => nav("/calculator")}>Re-take Assessment</Button>
          <Button className="bg-slate-700">Download Result</Button>
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          No personal identifiers stored. This tool is for educational information and is not a medical diagnosis.
        </p>
      </div>
    </Card>
  );
}
