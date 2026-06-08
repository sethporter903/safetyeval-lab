export type Summary = {
  suite_count: number;
  case_count: number;
  run_count: number;
  provider_count: number;
  latest_pass_rate: number;
};

export type LegacyEvalResult = {
  id: number;
  case_id: number;
  output: string;
  verdict: 'pass' | 'fail';
  score: number;
  rationale: string;
  created_at: string;
};

export type LegacyEvalRun = {
  id: number;
  suite_id: number;
  provider_id: number;
  model_name: string;
  status: string;
  pass_rate: number;
  total_cases: number;
  passed_cases: number;
  created_at: string;
  results: LegacyEvalResult[];
};

export type FileEvalCase = {
  id: string;
  category: string;
  prompt: string;
  expected_behavior: string;
  severity: string;
  tags: string[];
};

export type FileEvalSuiteSummary = {
  name: string;
  case_count: number;
  categories: string[];
  severities: string[];
};

export type FileEvalSuite = FileEvalSuiteSummary & {
  cases: FileEvalCase[];
};

export type Provider = {
  name: string;
  display_name: string;
  default_model: string;
  requires_api_key: boolean;
};

export type EvalRunCreate = {
  suite_name: string;
  provider: string;
  model?: string | null;
  max_cases?: number | null;
};

export type EvalRunCreated = {
  run_id: number;
  suite_name: string;
  provider: string;
  model: string;
  status: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  pass_rate: number;
};

export type EvalRunDetail = EvalRunCreated & {
  created_at: string;
};

export type EvalResultDetail = {
  result_id: number;
  case_id: number;
  case_title: string;
  category: string;
  severity: string;
  prompt: string;
  expected_behavior: string;
  model_response: string;
  verdict: 'pass' | 'fail';
  score: number;
  safety_label: 'safe' | 'borderline' | 'unsafe';
  risk_score: number;
  refusal_detected: boolean;
  safe_alternative_detected: boolean;
  rationale: string;
  review_status: 'unreviewed' | 'pass' | 'review' | 'fail';
  reviewer_notes: string;
  reviewed_at: string | null;
};

export type EvalResultReviewUpdate = {
  review_status: 'pass' | 'review' | 'fail';
  reviewer_notes: string;
};

export type EvalResultReview = {
  result_id: number;
  review_status: 'pass' | 'review' | 'fail';
  reviewer_notes: string;
  reviewed_at: string;
};

export type FailedCaseSummary = {
  result_id: number;
  case_id: number;
  case_title: string;
  category: string;
  severity: string;
  safety_label: 'safe' | 'borderline' | 'unsafe';
  risk_score: number;
  rationale: string;
};

export type EvalRunScoreSummary = {
  run_id: number;
  total_cases: number;
  pass_rate: number;
  unsafe_rate: number;
  borderline_rate: number;
  average_risk_score: number;
  severity_weighted_risk_score: number;
  failure_rate_by_category: Record<string, number>;
  refusal_quality_score: number;
  top_failed_cases: FailedCaseSummary[];
};

export type EvalRunComparisonItem = {
  run_id: number;
  suite_name: string;
  provider: string;
  model: string;
  status: string;
  total_cases: number;
  pass_rate: number;
  unsafe_rate: number;
  average_risk_score: number;
  failure_rate_by_category: Record<string, number>;
};

export type EvalRunCategoryComparison = {
  category: string;
  failure_rates: Record<string, number>;
};

export type EvalRunComparison = {
  runs: EvalRunComparisonItem[];
  category_breakdown: EvalRunCategoryComparison[];
};
