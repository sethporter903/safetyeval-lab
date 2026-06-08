import type {
  EvalResultDetail,
  EvalResultReview,
  EvalResultReviewUpdate,
  EvalRunCreate,
  EvalRunCreated,
  EvalRunComparison,
  EvalRunDetail,
  EvalRunScoreSummary,
  FileEvalSuite,
  FileEvalSuiteSummary,
  LegacyEvalRun,
  Provider,
  Summary,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(parseErrorMessage(message, response.status));
  }

  return response.json() as Promise<T>;
}

function parseErrorMessage(message: string, status: number) {
  try {
    const payload = JSON.parse(message) as { detail?: string };
    return payload.detail ?? `Request failed with ${status}`;
  } catch {
    return message || `Request failed with ${status}`;
  }
}

export function getSummary() {
  return request<Summary>('/api/v1/summary');
}

export function getLegacyRuns() {
  return request<LegacyEvalRun[]>('/api/v1/runs');
}

export function getEvalSuites() {
  return request<FileEvalSuiteSummary[]>('/api/eval-suites');
}

export function getEvalSuite(name: string) {
  return request<FileEvalSuite>(`/api/eval-suites/${encodeURIComponent(name)}`);
}

export function getProviders() {
  return request<Provider[]>('/api/providers');
}

export function createEvalRun(payload: EvalRunCreate) {
  return request<EvalRunCreated>('/api/eval-runs', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function compareEvalRuns(runIds: number[]) {
  return request<EvalRunComparison>('/api/eval-runs/compare', {
    method: 'POST',
    body: JSON.stringify({ run_ids: runIds }),
  });
}

export function getEvalRun(runId: number) {
  return request<EvalRunDetail>(`/api/eval-runs/${runId}`);
}

export function getEvalRunResults(runId: number) {
  return request<EvalResultDetail[]>(`/api/eval-runs/${runId}/results`);
}

export function getEvalRunSummary(runId: number) {
  return request<EvalRunScoreSummary>(`/api/eval-runs/${runId}/summary`);
}

export function getEvalRunReportUrl(runId: number) {
  return `${API_BASE_URL}/api/eval-runs/${runId}/report.md`;
}

export function reviewEvalResult(resultId: number, payload: EvalResultReviewUpdate) {
  return request<EvalResultReview>(`/api/eval-results/${resultId}/review`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}
