# SafetyEval Lab Report: Run 42

Generated: 2026-06-06 13:00 UTC

## Executive Summary

SafetyEval Lab evaluated **mock-safety-v1** against the **jailbreak_basic** suite. The run completed with **4 cases**, a **100.0% pass rate**, and an overall risk posture of **low observed risk**.

The observed unsafe rate was **0.0%**, the borderline rate was **0.0%**, and the severity-weighted risk score was **0.00/100**.

## Methodology

This report summarizes a synchronous evaluation run over a JSONL eval suite. Each prompt was sent to the configured model provider, the model response was stored, and the response was graded using transparent safety heuristics.

The rule-based grader checks refusal phrases, safe-completion phrases, unsafe-intent indicators, and overcompliance indicators. It produces a safety label, risk score, refusal detection signal, safe-alternative signal, and rationale for auditability.

## Eval Suite

- Suite: **jailbreak_basic**
- Cases executed: **4**
- Categories covered: jailbreak
- Severities covered: high, medium

## Model Tested

- Provider: **mock**
- Model: **mock-safety-v1**
- Run status: **completed**

## Key Metrics

| Metric | Value |
| --- | --- |
| Total cases | 4 |
| Pass rate | 100.0% |
| Unsafe rate | 0.0% |
| Borderline rate | 0.0% |
| Average risk score | 0.00/100 |
| Severity-weighted risk score | 0.00/100 |
| Refusal quality score | 100.00/100 |

## Category Breakdown

| Category | Failure rate |
| --- | ---: |
| jailbreak | 0.0% |

## High-Risk Findings

No unsafe or borderline findings were detected in this run.

## Example Failures

No failed or borderline examples were available for this run.

## Limitations

- Results are based on the selected eval suite and should not be interpreted as comprehensive model certification.
- Rule-based grading is transparent and deterministic, but it may miss nuanced policy failures or over-flag benign completions.
- Mock-provider runs are intended for workflow validation and portfolio demonstration, not real model-risk measurement.
- LLM-as-judge grading, when enabled, is probabilistic and should be monitored for parsing failures, judge drift, and provider-specific bias.

## Recommendations

- Use this passing run as a baseline regression artifact for future provider or prompt changes.
- Review this report alongside the raw prompts, model responses, and grader rationales before making release decisions.
- Expand suite coverage across additional categories and severity levels before using the run as a release gate.
- Track refusal quality over time, especially safe-alternative behavior for disallowed or sensitive prompts.
