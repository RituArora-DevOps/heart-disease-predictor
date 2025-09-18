import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from 'react-router-dom'
import { postPredict } from '../api/client'
import { useResult } from '../state/ResultContext'
import Card from '../components/Card'
import Field from '../components/Field'
import Button from '../components/Button'
import clsx from 'clsx'

const schema = z.object({
  age: z.coerce.number().min(20).max(79),
  sex: z.enum(['M', 'F']),
  systolic_bp: z.coerce.number().min(90).max(200),
  on_bp_meds: z.enum(['0', '1']),
  total_chol: z.coerce.number().min(130).max(320),
  hdl_chol: z.coerce.number().min(20).max(100),
  ldl_chol: z.coerce.number().min(30).max(300).optional(),
  diabetes: z.enum(['0', '1']),
  smoker: z.enum(['current', 'former', 'never']),
})

export default function Calculator() {
  const nav = useNavigate()
  const { setResult } = useResult()
  const {
    register,
    setValue,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { sex: 'M', on_bp_meds: '0', smoker: 'never', diabetes: '0' },
  })

  const onSubmit = async (v) => {
    const payload = {
      age: v.age,
      sex: v.sex,
      systolic_bp: v.systolic_bp,
      on_bp_meds: Number(v.on_bp_meds),
      total_chol: v.total_chol,
      hdl_chol: v.hdl_chol,
      ldl_chol: v.ldl_chol ?? undefined,
      diabetes: v.diabetes ? Number(v.diabetes) : undefined,
      smoker: v.smoker || undefined,
    }
    const res = await postPredict(payload)
    setResult(res)
    nav('/results')
  }

  return (
    <Card title="Assess Your Risk">
      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-x-10 gap-y-6 md:grid-cols-2">
        <Field label="Age" required error={errors.age?.message}>
          <input
            className="input w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900"
            type="number"
            {...register('age')}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be between 20–79</p>
        </Field>

        <Field label="Sex" required>
          <Segment
            name="sex"
            setValue={setValue}
            options={[
              ['M', 'Male'],
              ['F', 'Female'],
            ]}
          />
        </Field>

        <Field
          label="Systolic Blood Pressure"
          unit="mmHg"
          required
          error={errors.systolic_bp?.message}
        >
          <input
            className="input w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900"
            type="number"
            {...register('systolic_bp')}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be between 90–200</p>
        </Field>

        <Field label="Currently taking blood-pressure medication?" required>
          <Segment
            name="on_bp_meds"
            setValue={setValue}
            options={[
              ['1', 'Yes'],
              ['0', 'No'],
            ]}
          />
        </Field>

        <Field label="Total Cholesterol" unit="mg/dL" required error={errors.total_chol?.message}>
          <input
            className="input w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900"
            type="number"
            {...register('total_chol')}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be between 130–320</p>
        </Field>

        <Field label="HDL Cholesterol" unit="mg/dL" required error={errors.hdl_chol?.message}>
          <input
            className="input w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900"
            type="number"
            {...register('hdl_chol')}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be between 20–100</p>
        </Field>

        <Field label="LDL Cholesterol (optional)" unit="mg/dL" error={errors.ldl_chol?.message}>
          <input
            className="input w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900"
            type="number"
            {...register('ldl_chol')}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be between 30-300</p>
        </Field>

        <Field label="Diabetes" required>
          <Segment
            name="diabetes"
            setValue={setValue}
            options={[
              ['1', 'Yes'],
              ['0', 'No'],
            ]}
          />
        </Field>

        <Field label="Smoker" required>
          <Segment
            name="smoker"
            setValue={setValue}
            options={[
              ['current', 'Current'],
              ['former', 'Former'],
              ['never', 'Never'],
            ]}
          />
        </Field>

        <div className="flex justify-center md:col-span-2">
          <Button size="lg" disabled={isSubmitting}>
            {isSubmitting ? 'Calculating…' : 'Calculate'}
          </Button>
        </div>
      </form>
    </Card>
  )
}

function Segment({ name, setValue, options }) {
  return (
    <div className="inline-flex overflow-hidden rounded-md border border-slate-300 bg-slate-200">
      {options.map(([val, label], idx) => (
        <button
          key={val}
          type="button"
          className={clsx(
            'px-4 py-2 text-sm font-semibold text-slate-700',
            idx === 0 && 'bg-navy text-white'
          )}
          onClick={(e) => {
            // visual active state
            const parent = e.currentTarget.parentElement
            ;[...parent.children].forEach((btn) => btn.classList.remove('bg-navy', 'text-white'))
            e.currentTarget.classList.add('bg-navy', 'text-white')
            setValue(name, val, { shouldValidate: true })
          }}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
