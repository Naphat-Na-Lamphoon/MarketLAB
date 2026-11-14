const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type HypothesisInput = {
  problem_statement: string;
  target_segment: string;
  offer_description: string;
  pricing_tier: string;
  budget_cap_thb: number;
};

export async function createHypothesis(input: HypothesisInput) {
  const response = await fetch(`${apiUrl}/api/v1/hypotheses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`Unable to create hypothesis (${response.status})`);
  }
  return response.json();
}

export type AssetDraft = {
  asset_id: string;
  hypothesis_id: string;
  headline: string;
  body: string;
  call_to_action: string;
  status: "DRAFT";
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
}

export function generateAsset(hypothesisId: string) {
  return request<AssetDraft>("/api/v1/assets/generate", {
    method: "POST",
    body: JSON.stringify({ hypothesis_id: hypothesisId }),
  });
}

export function createExperiment(hypothesisId: string) {
  return request<{ experiment_id: string }>("/api/v1/experiments", {
    method: "POST",
    body: JSON.stringify({ hypothesis_id: hypothesisId, channel_type: "simulated" }),
  });
}

export function approveExperiment(experimentId: string, budgetCap: number) {
  return request(`/api/v1/experiments/${experimentId}/approve`, {
    method: "POST",
    body: JSON.stringify({
      approved_by_user_id: "00000000-0000-0000-0000-000000000001",
      budget_cap_thb: budgetCap,
    }),
  });
}

export function launchExperiment(experimentId: string) {
  return request<{ status: string }>(`/api/v1/experiments/${experimentId}/launch`, {
    method: "POST",
  });
}
