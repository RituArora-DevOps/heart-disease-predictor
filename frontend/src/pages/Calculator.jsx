import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { postPredict } from "../api/client";
import { useResult } from "../state/ResultContext";
import Card from "../components/Card";
import Field from "../components/Field";
import Button from "../components/Button";
import Segment from "../components/Segment";

const HEALTH_OPTIONS = ["Poor", "Fair", "Good", "Very Good", "Excellent"];
const AGE_GROUPS = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80+"];
const CHECKUP_OPTIONS = ["Never", "5 or more years ago", "Within the past 5 years", "Within the past 2 years", "Within the past year"];
const DIABETES_OPTIONS = ["No", "No, pre-diabetes or borderline diabetes", "Yes, but female told only during pregnancy", "Yes"];
const SEX_OPTIONS = ["Female", "Male"];

const schema = z.object({
  General_Health: z.enum(HEALTH_OPTIONS),
  Checkup: z.enum(CHECKUP_OPTIONS),
  Exercise: z.enum(["0", "1"]),
  Skin_Cancer: z.enum(["0", "1"]),
  Other_Cancer: z.enum(["0", "1"]),
  Depression: z.enum(["0", "1"]),
  Diabetes: z.enum(DIABETES_OPTIONS),
  Arthritis: z.enum(["0", "1"]),
  Sex: z.enum(SEX_OPTIONS),
  Age_Category: z.enum(AGE_GROUPS),

  Height_cm: z.coerce.number().min(0, { message: "Must be ≥ 0" }),
  Weight_kg: z.coerce.number().min(0, { message: "Must be ≥ 0" }),

  Smoking_History: z.enum(["0", "1"]),
  Alcohol_Consumption: z.coerce.number().min(0),
  Fruit_Consumption: z.coerce.number().min(0),
  Green_Vegetables_Consumption: z.coerce.number().min(0),
  FriedPotato_Consumption: z.coerce.number().min(0),
});

export default function Calculator() {
  const nav = useNavigate();
  const { setResult } = useResult();

  const {
    register,
    setValue,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      General_Health: "Good",
      Age_Category: "45-49",
      Sex: "Female",
      Checkup: "Never",
      Exercise: "1",
      Skin_Cancer: "0",
      Other_Cancer: "0",
      Depression: "0",
      Diabetes: "No",
      Arthritis: "0",
      Height_cm: 170,
      Weight_kg: 70,
      Smoking_History: "0",
      Alcohol_Consumption: 0,
      Fruit_Consumption: 1,
      Green_Vegetables_Consumption: 1,
      FriedPotato_Consumption: 0,
    },
  });

  const onSubmit = async (v) => {
    const yn = (x) => (String(x) === "1" ? "Yes" : "No");

    const payload = {
      General_Health: v.General_Health,
      Checkup: v.Checkup,

      Exercise: yn(v.Exercise),
      Skin_Cancer: yn(v.Skin_Cancer),
      Other_Cancer: yn(v.Other_Cancer),
      Depression: yn(v.Depression),
      Arthritis: yn(v.Arthritis),
      Smoking_History: yn(v.Smoking_History),

      Diabetes: v.Diabetes,
      Sex: v.Sex,
      Age_Category: v.Age_Category,

      Height_cm: Number(v.Height_cm),
      Weight_kg: Number(v.Weight_kg),

      Alcohol_Consumption: Number(v.Alcohol_Consumption),
      Fruit_Consumption: Number(v.Fruit_Consumption),
      Green_Vegetables_Consumption: Number(v.Green_Vegetables_Consumption),
      FriedPotato_Consumption: Number(v.FriedPotato_Consumption),
    };

    const res = await postPredict(payload);

    setResult({ ...res, input: payload });
    nav("/results");
  };

  return (
    <Card title="Assess Your Risk">
      <form onSubmit={handleSubmit(onSubmit)} className="grid max-h-[70vh] gap-x-10 gap-y-6 overflow-y-auto pr-1 md:grid-cols-4">
        <Field label="General health" error={errors.General_Health?.message}>
          <select className="input h-9.5 w-full rounded-md border border-slate-300 px-3 text-slate-900 md:w-28" {...register("General_Health")}>
            {HEALTH_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Sex" error={errors.Sex?.message}>
          <select className="input h-9.5 w-full rounded-md border border-slate-300 px-3 text-slate-900 md:w-28" {...register("Sex")}>
            {SEX_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Age group" error={errors.Age_Category?.message}>
          <select className="input h-9.5 w-full rounded-md border border-slate-300 px-3 text-slate-900 md:w-28" {...register("Age_Category")}>
            {AGE_GROUPS.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Recent medical checkup" error={errors.Checkup?.message}>
          <select className="input h-9.5 w-full rounded-md border border-slate-300 px-3 text-slate-900 md:w-28" {...register("Checkup")}>
            {CHECKUP_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Exercise regularly" error={errors.Exercise?.message}>
          <Segment
            name="Exercise"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Smoking history" error={errors.Smoking_History?.message}>
          <Segment
            name="Smoking_History"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Alcohol consumption" error={errors.Alcohol_Consumption?.message}>
          <Segment
            name="Alcohol_Consumption"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Fruit consumption" error={errors.Fruit_Consumption?.message}>
          <Segment
            name="Fruit_Consumption"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Green vegetables consumption" error={errors.Green_Vegetables_Consumption?.message}>
          <Segment
            name="Green_Vegetables_Consumption"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Fried potato consumption" error={errors.FriedPotato_Consumption?.message}>
          <Segment
            name="FriedPotato_Consumption"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Height" unit="cm" error={errors.Height_cm?.message}>
          <input
            className="input h-9.5 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 md:w-28"
            type="number"
            step="0.1"
            min={0}
            {...register("Height_cm")}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be ≥ 0</p>
        </Field>

        <Field label="Weight" unit="kg" error={errors.Weight_kg?.message}>
          <input
            className="input h-9.5 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 md:w-28"
            type="number"
            step="0.1"
            min={0}
            {...register("Weight_kg")}
          />
          <p className="mt-1 text-xs text-slate-500 italic">Value must be ≥ 0</p>
        </Field>

        <Field label="History of skin cancer" error={errors.Skin_Cancer?.message}>
          <Segment
            name="Skin_Cancer"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="History of other cancers" error={errors.Other_Cancer?.message}>
          <Segment
            name="Other_Cancer"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="History of depression" error={errors.Depression?.message}>
          <Segment
            name="Depression"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <Field label="Diabetes" error={errors.Diabetes?.message}>
          <select className="input h-9.5 w-full rounded-md border border-slate-300 px-3 text-slate-900 md:w-28" {...register("Diabetes")}>
            {DIABETES_OPTIONS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Arthritis" error={errors.Arthritis?.message}>
          <Segment
            name="Arthritis"
            setValue={setValue}
            options={[
              ["0", "No"],
              ["1", "Yes"],
            ]}
          />
        </Field>

        <div className="flex justify-center md:col-span-4">
          <Button type="submit" size="lg" disabled={isSubmitting}>
            {isSubmitting ? "Calculating…" : "Calculate"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
