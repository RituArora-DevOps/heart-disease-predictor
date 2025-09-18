import { useEffect, useState } from "react";

const CATEGORIES = [
  {
    id: "smoking",
    title: "Quit smoking",
    emoji: "🚭",
    resources: [
      {
        title: "Toxins in Tobacco Smoke",
        source: "Public Health Agency of Canada",
        url: "https://www.canada.ca/en/health-canada/services/health-concerns/tobacco/legislation/tobacco-product-labelling/tobacco-smoke-toxins.html",
      },
      {
        title: "Quit with confidence: Guide to a smoke-free life",
        source: "Public Health Agency of Canada",
        url: "https://www.canada.ca/en/health-canada/services/smoking-tobacco/quit-smoking/introduction.html",
      },
    ],
  },
  {
    id: "diet",
    title: "Follow a healthy eating pattern",
    emoji: "🥗",
    resources: [
      {
        title: "Healthy eating basics",
        source: "Heart & Stroke Foundation of Canada",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-eating/healthy-eating-basics",
      },
      {
        title: "Vegetables and fruit",
        source: "Heart & Stroke Foundation of Canada",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-eating/vegetables-and-fruit",
      },
    ],
  },
  {
    id: "activity",
    title: "Incorporate regular physical activity into your routine",
    emoji: "🏃‍♂️",
    resources: [
      {
        title: "The benefits of physical activity",
        source: "Public Health Agency of Canada",
        url: "https://www.heartandstroke.ca/healthy-living/stay-active/benefits-of-physical-activity",
      },
      {
        title: "Physical Activity Tips for Adults",
        source: "Public Health Agency of Canada",
        url: "https://www.canada.ca/en/public-health/services/publications/healthy-living/physical-activity-tips-adults-18-64-years.html",
      },
    ],
  },
  {
    id: "weight",
    title: "Achieve and maintain a healthy weight",
    emoji: "⚖️",
    resources: [
      {
        title: "Achieving and maintaining a healthy weight",
        source: "Heart & Stroke Foundation of Canada",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-weight/maintaining-a-healthy-weight",
      },
      {
        title: "Healthy weight and waist",
        source: "Heart & Stroke Foundation of Canada",
        url: "https://www.heartandstroke.ca/healthy-living/healthy-weight/healthy-weight-and-waist",
      },
    ],
  },
  {
    id: "alcohol",
    title: "Limit your intake of alcohol",
    emoji: "🍸",
    resources: [
      {
        title: "Preventing Alcohol-Related Harms",
        source: "CDC — Heart Disease, High Blood Pressure, Cholesterol & Tobacco",
        url: "https://www.cdc.gov/alcohol/prevention/index.html",
      },
      {
        title: "Preventing Excessive Alcohol Use with Proven Strategies",
        source: "CDC — Heart Disease, High Blood Pressure, Cholesterol & Tobacco",
        url: "https://www.cdc.gov/alcohol/prevention/proven-strategies.html",
      },
    ],
  },
  {
    id: "meds",
    title: "Blood pressure-lowering and/or lipid-modifying medicines",
    emoji: "💊",
    resources: [
      {
        title: "How do I monitor my blood pressure?",
        source: "Hypertension Canada",
        url: "https://hypertension.ca/how-do-i-monitor-my-bp/",
      },
      {
        title: "How do I maintain a healthy blood pressure?",
        source: "Hypertension Canada",
        url: "https://hypertension.ca/how-do-i-maintain-healthy-bp/",
      },
    ],
  },
];

export default function Resources() {
  const [openCat, setOpenCat] = useState(null);
  const active = CATEGORIES.find((c) => c.id === openCat);

  useEffect(() => {
    if (openCat) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => (document.body.style.overflow = "");
  }, [openCat]);

  return (
    <section className="container py-10">
      <h1 className="-ml-10 text-3xl font-bold text-white md:text-3xl">How to lower your risk</h1>

      <div className="mt-10 -mr-10 -ml-10 grid gap-8 md:grid-cols-12 lg:gap-10">
        {CATEGORIES.map((c) => (
          <article
            key={c.id}
            className="container min-h-[170px] rounded-2xl bg-[#c5dbe8] p-6 shadow ring-1 ring-[#c9dff3] transition hover:-translate-y-0.5 hover:shadow-lg md:col-span-6 md:min-h-[190px] md:p-7 xl:col-span-4">
            <button
              onClick={() => setOpenCat(c.id)}
              className="group flex w-full cursor-pointer items-start justify-between gap-4 text-left"
              aria-haspopup="dialog">
              <div>
                <h2 className="md:text-ml text-lg font-semibold text-black transition-colors transition-transform duration-150 group-hover:text-[#e7850F]">
                  {c.title}
                </h2>
                <p className="mt-1 text-xs text-black">Trusted tips & resources</p>
              </div>
              <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#a5c5df] text-xl">{c.emoji}</span>
            </button>
          </article>
        ))}
      </div>

      {active && <ResourcesModal category={active} onClose={() => setOpenCat(null)} />}
    </section>
  );
}

function ResourcesModal({ category, onClose }) {
  useEffect(() => {
    const onEsc = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onEsc);
    return () => window.removeEventListener("keydown", onEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[100]" role="dialog" aria-modal="true" aria-labelledby="res-modal-title">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="animate-in fade-in zoom-in-95 w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-black/10 duration-150">
          <div className="flex items-center justify-between border-b px-6 py-4">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-[#a5c5df] text-xl">{category.emoji}</span>
              <h3 id="res-modal-title" className="text-lg font-semibold text-[#0b3b66]">
                {category.title}
              </h3>
            </div>
            <button onClick={onClose} className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700" aria-label="Close">
              <svg viewBox="0 0 20 20" className="h-5 w-5" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>

          <div className="max-h-[70vh] space-y-3 overflow-auto px-6 py-5">
            {category.resources?.length ?
              category.resources.map((r, i) => <ResourceItem key={i} {...r} />)
            : <p className="text-sm text-slate-600">
                Add links for this module in <code>CATEGORIES[{category.id}]</code>.
              </p>
            }
          </div>
        </div>
      </div>
    </div>
  );
}

function ResourceItem({ title, source, url = "#" }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg border border-slate-300 bg-white px-4 py-3 transition hover:bg-slate-100">
      <div className="flex items-start justify-between gap-3">
        <p className="text-navy text-sm font-semibold">{title}</p>
        <svg className="mt-0.5 h-4 w-4 text-slate-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path d="M11 3h6v6h-2V6.41l-7.29 7.3-1.42-1.42L13.59 5H11V3Z" />
          <path d="M5 5h4v2H7v6h6v-2h2v4H5V5Z" />
        </svg>
      </div>
      {source && <p className="mt-1 text-xs text-slate-500">{source}</p>}
    </a>
  );
}
