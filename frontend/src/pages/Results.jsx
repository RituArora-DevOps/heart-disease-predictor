import Card from "../components/Card";
import Button from "../components/Button";
import { useResult } from "../state/ResultContext";
import { Link, useNavigate } from "react-router-dom";

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export default function Results() {
  const { result } = useResult();
  const nav = useNavigate();

  if (!result) {
    return (
      <Card title="No result" className="min-h-[420px]">
        <p>Please run the calculator first.</p>
      </Card>
    );
  }

  const prob = Number(result?.probability ?? 0); // 0~1
  const pred = Number(result?.prediction ?? 0); // 0 or 1
  const thr = Number(result?.threshold_used ?? 0.5); // e.g. 0.202
  const percent = `${(prob * 100).toFixed(2)}%`;

  const status = pred === 1 ? "High Risk of Heart Disease" : "Low Risk of Heart Disease";
  const statusColor = pred === 1 ? "bg-red-100 text-red-800 border-red-200" : "bg-green-100 text-green-800 border-green-200";

  const input = result.input || {};

  const handleDownload = () => {
    if (!input || Object.keys(input).length === 0) {
      alert("No form data found. Please re-run the assessment and try again.");
      return;
    }

    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const lineHeight = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    const marginX = 48;
    let y = 56;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("CardioRisk — Assessment Result", marginX, y);
    y += 18;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, marginX, y);
    y += 28;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("Your Result", marginX, y);
    y += 18;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(13);
    doc.text(`Estimated Risk Probability: ${percent}`, marginX, y);
    y += lineHeight;
    doc.text(`Risk Status: ${status}`, marginX, y);
    y += lineHeight;
    doc.text(`Model Threshold: ${thr}`, marginX, y);
    y += 30;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("Your Inputs", marginX, y);
    y += 14;

    const label = (k) =>
      ({
        General_Health: "General health",
        Checkup: "Recent medical checkup",
        Exercise: "Exercise regularly",
        Skin_Cancer: "History of skin cancer",
        Other_Cancer: "History of other cancers",
        Depression: "History of depression",
        Diabetes: "Diabetes",
        Arthritis: "Arthritis",
        Sex: "Sex",
        Age_Category: "Age group",
        Height_cm: "Height (cm)",
        Weight_kg: "Weight (kg)",
        Smoking_History: "Smoking history",
        Alcohol_Consumption: "Alcohol consumption",
        Fruit_Consumption: "Fruit consumption",
        Green_Vegetables_Consumption: "Green vegetables consumption",
        FriedPotato_Consumption: "Fried potato consumption",
      })[k] || k;

    const inputOrder = [
      "General_Health",
      "Sex",
      "Age_Category",
      "Checkup",
      "Exercise",
      "Smoking_History",
      "Alcohol_Consumption",
      "Fruit_Consumption",
      "Green_Vegetables_Consumption",
      "FriedPotato_Consumption",
      "Height_cm",
      "Weight_kg",
      "Skin_Cancer",
      "Other_Cancer",
      "Depression",
      "Diabetes",
      "Arthritis",
    ];

    const rows = inputOrder.filter((k) => k in input).map((k) => [label(k), String(input[k])]);

    autoTable(doc, {
      startY: y,
      head: [["Field", "Value"]],
      body: rows,
      styles: { fontSize: 10, cellPadding: 6 },
      headStyles: { fillColor: [30, 41, 59] },
      margin: { left: marginX, right: marginX },
      tableWidth: pageWidth - marginX * 2,
      didDrawPage: (data) => {
        y = data.cursor.y + 28;
      },
    });

    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("How to lower your risk", marginX, y);
    y += 18;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(13);

    const bullets = [
      {
        text: "Healthy eating pattern",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-eating/healthy-eating-basics",
      },
      {
        text: "Regular physical activity",
        url: "https://www.canada.ca/en/public-health/services/publications/healthy-living/physical-activity-tips-adults-18-64-years.html",
      },
      {
        text: "Maintain a healthy weight",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-weight/maintaining-a-healthy-weight",
      },
      {
        text: "Limit intake of alcohol",
        url: "https://www.cdc.gov/alcohol/prevention/proven-strategies.html",
      },
    ];

    bullets.forEach((b) => {
      doc.text("•", marginX, y);
      doc.textWithLink(b.text, marginX + 12, y, { url: b.url });
      y += lineHeight;
      if (y > doc.internal.pageSize.getHeight() - 72) {
        doc.addPage();
        y = 56;
      }
    });

    const footer = "CardioRisk — educational tool (not a medical diagnosis)";
    doc.setFontSize(9);
    const textWidth = doc.getTextWidth(footer);
    doc.text(footer, (pageWidth - textWidth) / 2, doc.internal.pageSize.getHeight() - 32);

    const date = new Date().toISOString().slice(0, 10);
    doc.save(`CardioRisk_Result_${date}.pdf`);
  };

  return (
    <Card title="Your Estimated Heart Disease Risk" panelClassName="max-w-[1000px] min-h-[520px] p-10" bodyClassName="flex h-full flex-col">
      <div className="flex h-full flex-col">
        <div className="mt-9 grid grid-cols-1 gap-16 md:grid-cols-2 max-w-[1050px] mx-auto">
          <div className="rounded-xl bg-white p-8 shadow-sm">
            <div className="flex flex-col items-center text-center space-y-3 md:space-y-4">
              <p className="text-3xl font-extrabold text-slate-900">{percent}</p>
              <p className="text-sm text-slate-600 leading-relaxed">Estimated Risk Probability</p>
              <span
                className={`inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-semibold ${statusColor}`}
                title={`Model threshold: ${thr}`}>
                {status}
              </span>
              <p className="text-xs text-slate-500 leading-relaxed">Model threshold: {thr}</p>
            </div>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-bold text-slate-800">How to lower your risk</h3>
            <ul className="text-sm leading-relaxed space-y-2">
              <li>
                <a
                  href="https://www.heartandstroke.ca/healthy-living/healthy-eating/healthy-eating-basics"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-700 hover:text-amber-600 underline-offset-2 hover:underline transition-colors">
                  Healthy eating pattern
                </a>
              </li>
              <li>
                <a
                  href="https://www.canada.ca/en/public-health/services/publications/healthy-living/physical-activity-tips-adults-18-64-years.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-700 hover:text-amber-600 underline-offset-2 hover:underline transition-colors">
                  Regular physical activity
                </a>
              </li>
              <li>
                <a
                  href="https://www.heartandstroke.ca/healthy-living/healthy-weight/maintaining-a-healthy-weight"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-700 hover:text-amber-600 underline-offset-2 hover:underline transition-colors">
                  Maintain a healthy weight
                </a>
              </li>
              <li>
                <a
                  href="https://www.cdc.gov/alcohol/prevention/proven-strategies.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-700 hover:text-amber-600 underline-offset-2 hover:underline transition-colors">
                  Limit intake of alcohol
                </a>
              </li>
            </ul>
            <Link
              to="/resources"
              className="mt-4 inline-block text-sm text-slate-700 underline underline-offset-2 hover:text-amber-600 hover:underline transition-colors">
              See more trusted resources
            </Link>
          </div>
        </div>

        <div className="mt-14 flex justify-center gap-3">
          <Button onClick={() => nav("/calculator")}>Re-take Assessment</Button>
          <Button className="bg-slate-700" onClick={handleDownload}>
            Download Result
          </Button>
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          No personal identifiers stored. This tool is for educational information and is not a medical diagnosis.
        </p>
      </div>
    </Card>
  );
}
