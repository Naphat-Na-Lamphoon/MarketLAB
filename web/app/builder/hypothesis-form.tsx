"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createHypothesis, type HypothesisInput } from "../../lib/api";

const initialForm: HypothesisInput = {
  problem_statement: "",
  target_segment: "",
  offer_description: "",
  pricing_tier: "",
  budget_cap_thb: 1000,
};

export default function HypothesisForm() {
  const router = useRouter();
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  function update(field: keyof HypothesisInput, value: string) {
    setForm((current) => ({ ...current, [field]: field === "budget_cap_thb" ? Number(value) : value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Saving...");
    try {
      const result = await createHypothesis(form);
      router.push(`/assets?hypothesisId=${result.hypothesis_id}&budget=${form.budget_cap_thb}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to save hypothesis");
    }
  }

  return (
    <form onSubmit={submit} className="form-card">
      <div className="form-grid">
      {([
        ["problem_statement", "Problem"],
        ["target_segment", "Target segment"],
        ["offer_description", "Offer"],
        ["pricing_tier", "Pricing"],
      ] as const).map(([field, label]) => (
        <label key={field} className={`field ${field === "problem_statement" || field === "offer_description" ? "full" : ""}`}>
          {label}
          <textarea required rows={3} value={form[field]} onChange={(event) => update(field, event.target.value)} />
        </label>
      ))}
      <label className="field">
        Budget cap (THB)
        <input min={1} required type="number" value={form.budget_cap_thb} onChange={(event) => update("budget_cap_thb", event.target.value)} />
      </label>
      </div>
      <div className="form-actions"><button className="button" type="submit">Save hypothesis draft</button><p className="notice" aria-live="polite">{message}</p></div>
    </form>
  );
}
