// frontend/src/pages/Results.jsx
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

  // ---------- NEW: Explanation logic ----------
  // Helpers to make age category comparisons resilient to labels like "65-69 years"
  const parseAgeLow = (ageLabel) => {
    if (!ageLabel || typeof ageLabel !== "string") return NaN;
    const m = ageLabel.match(/\d+/);
    return m ? Number(m[0]) : NaN;
  };
  const isOlder = (ageLabel, min) => {
    const low = parseAgeLow(ageLabel);
    return Number.isFinite(low) && low >= min;
  };
  const isYounger = (ageLabel, max) => {
    const low = parseAgeLow(ageLabel);
    return Number.isFinite(low) && low <= max;
  };

  const getRiskExplanation = (inputObj, prediction) => {
    const explanations = [];
    const highRisk = prediction === 1;

    const formatBool = (val) => (val === "Yes" ? "Present" : "Absent");

    // 1) Age (highest impact heuristically)
    const age = inputObj.Age_Category;
    if (age) {
      if (highRisk && isOlder(age, 60)) {
        explanations.push(`Age is a key driver: your age category (${age}) contributed significantly to the higher predicted risk.`);
      } else if (!highRisk && isYounger(age, 34)) {
        explanations.push(`Age is protective: your younger age category (${age}) helped lower the risk score.`);
      }
    }

    // 2) General Health
    const health = inputObj.General_Health;
    if (health) {
      if (highRisk && (health === "Poor" || health === "Fair")) {
        explanations.push("Self-reported general health is Poor/Fair, which strongly elevates cardiovascular risk in population data.");
      } else if (!highRisk && (health === "Excellent" || health === "Very good")) {
        explanations.push(`General health is ${health}, which provided a protective signal.`);
      }
    }

    // 3) BMI & Age interaction (derived)
    const height = Number(inputObj.Height_cm);
    const weight = Number(inputObj.Weight_kg);
    if (height > 0 && weight > 0) {
      const bmi = weight / (height / 100) ** 2;
      const bmiStatus =
        bmi >= 30 ? "Obese"
        : bmi >= 25 ? "Overweight"
        : "Normal";

      if (highRisk && bmi >= 25 && isOlder(age, 55)) {
        explanations.push(`Your BMI is ${bmiStatus}; combined with age, this amplified the predicted risk (BMI–Age interaction).`);
      } else if (!highRisk && bmi < 25) {
        explanations.push(`A healthy BMI (${bmiStatus}) acted as a protective factor.`);
      }
    }

    // 4) Sex
    const sex = inputObj.Sex;
    if (sex && highRisk && sex === "Male") {
      explanations.push(`Biological sex (${sex}) is associated with a higher baseline risk in this model.`);
    }

    // 5) Lifestyle / comorbidities
    const smoking = inputObj.Smoking_History; // "Yes"/"No"
    const exercise = inputObj.Exercise; // "Yes"/"No"
    const arthritis = inputObj.Arthritis; // "Yes"/"No"

    if (highRisk) {
      if (smoking === "Yes") {
        explanations.push("Smoking history is Present, a high-ranking risk factor in epidemiological data.");
      } else if (exercise === "No") {
        explanations.push("Lack of regular exercise is a strong risk factor and raises incidence in the data.");
      } else if (arthritis === "Yes") {
        explanations.push(`Arthritis is ${formatBool(arthritis)}, indicating chronic inflammation, which elevates risk.`);
      }
    } else {
      if (exercise === "Yes") {
        explanations.push("Regular physical activity is a strong protective factor and helped lower your risk.");
      } else if (smoking === "No") {
        explanations.push(`Smoking history is ${formatBool(smoking)}, which contributed a protective signal.`);
      }
    }

    if (explanations.length === 0) {
      return ["The prediction reflects a balanced combination of factors; no single factor dominated the result."];
    }
    return explanations.slice(0, 5);
  };

  const explanations = getRiskExplanation(input, pred);
  // ---------- END: Explanation logic ----------

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

    // 工具：在固定宽度内渲染“带圆点的换行段落”（与表格同宽）
    const writeWrappedBullet = (text) => {
      const indent = 12; // 圆点到正文的缩进
      const maxWidth = pageWidth - marginX * 2 - indent; // 与表格同宽（扣掉缩进）
      const pageHeight = doc.internal.pageSize.getHeight();
      const lines = doc.splitTextToSize(text, maxWidth);

      lines.forEach((ln, idx) => {
        if (y > pageHeight - 72) {
          doc.addPage();
          y = 56;
        }
        if (idx === 0) {
          doc.text("•", marginX, y);
          doc.text(ln, marginX + indent, y);
        } else {
          doc.text(ln, marginX + indent, y);
        }
        y += lineHeight;
      });
    };

    // Title + date
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("CardioRisk — Assessment Result", marginX, y);
    y += 18;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, marginX, y);
    y += 28;

    // Result
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

    // Inputs
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

    // Key factors
    y += 10;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(14);
    doc.text("Key Factors Influencing Your Result", marginX, y);
    y += 18;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(13);

    const explanationHeader = pred === 1 ? "The main factors driving your risk score up were:" : "The main protective factors lowering your risk were:";
    writeWrappedBullet(explanationHeader);

    explanations.forEach((exp) => {
      writeWrappedBullet(exp);
    });

    y += 10;

    // How to lower your risk
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
      const indent = 12;
      const maxWidth = pageWidth - marginX * 2 - indent;
      const pageHeight = doc.internal.pageSize.getHeight();
      const lines = doc.splitTextToSize(b.text, maxWidth);

      lines.forEach((ln, idx) => {
        if (y > pageHeight - 72) {
          doc.addPage();
          y = 56;
        }
        if (idx === 0) {
          doc.text("•", marginX, y);
          doc.textWithLink(ln, marginX + indent, y, { url: b.url });
        } else {
          doc.text(ln, marginX + indent, y);
        }
        y += lineHeight;
      });
    });

    // Footer
    const footer = "CardioRisk — educational tool (not a medical diagnosis)";
    doc.setFontSize(9);
    const textWidth = doc.getTextWidth(footer);
    doc.text(footer, (pageWidth - textWidth) / 2, doc.internal.pageSize.getHeight() - 32);

    const date = new Date().toISOString().slice(0, 10);
    doc.save(`CardioRisk_Result_${date}.pdf`);
  };

  return (
    <Card title="Your Estimated Heart Disease Risk" panelClassName="max-w-[1280px] min-h-[520px] p-10" bodyClassName="flex h-full flex-col">
      <div className="flex h-full flex-col">
        <div className="mt-9 grid grid-cols-1 gap-16 md:grid-cols-3 max-w-[1240px] mx-auto">
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

          <div className="rounded-xl bg-white p-8 shadow-sm">
            <h3 className="mb-3 font-bold text-slate-800">Key factors behind your result</h3>
            <ul className="list-disc pl-5 text-sm leading-relaxed space-y-1">
              {explanations.map((e, idx) => (
                <li key={idx} className="text-slate-700">
                  {e}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-xl bg-white p-8 shadow-sm">
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
