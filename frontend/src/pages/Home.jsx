import { Link } from 'react-router-dom'
import Button from '../components/Button'
import hero from '../assets/hero.PNG'

export default function Home() {
  return (
    <section className="container grid items-start gap-y-12 py-16 md:grid-cols-12 md:gap-x-14 lg:gap-x-18 lg:py-28">
      <div className="-ml-1 md:col-start-1 md:col-end-7 md:-ml-1.5 lg:-ml-11">
        <p className="text-[15px] font-bold tracking-widest text-[#14c36c] md:text-[15px]">
          For Heart Health Awareness
        </p>

        <h1 className="mt-8 text-5xl leading-[1.25] font-extrabold tracking-[0.06em] text-white md:text-5xl">
          Estimate your Heart Disease Risk
        </h1>

        <p className="mt-8 mb-2 max-w-xl text-base leading-relaxed text-slate-200 md:text-[20px]">
          Answer a few questions about your health to get an easy-to-read risk estimate -- along
          with trusted tips to improve heart health.
        </p>

        <Link to="/calculator" className="mt-8 inline-block">
          <Button size="lg">Calculate Now</Button>
        </Link>
      </div>

      <div className="-mr-1 hidden md:col-start-7 md:col-end-13 md:-mt-6 md:-mr-1.5 md:block lg:-mt-10 lg:-mr-9">
        <div className="relative h-[300px] w-full overflow-hidden rounded-2xl shadow-sm md:h-[460px] lg:h-[520px]">
          <img
            src={hero}
            alt="Heart health illustration"
            className="absolute inset-0 h-full w-full object-cover object-center"
          />
        </div>
      </div>
    </section>
  )
}
