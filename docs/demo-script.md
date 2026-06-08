# SafetyEval Lab Demo Script

Target length: 2 minutes.

## 0:00-0:15 - Problem and Positioning

"SafetyEval Lab is a lightweight AI safety evaluation platform for testing model behavior before deployment. It focuses on structured evals, transparent grading, model comparison, and investigator-style reporting for safety and trust teams."

## 0:15-0:35 - Eval Suites

Open the Eval Suites page.

"The eval suites are stored as JSONL files. Each case has an ID, category, prompt, expected behavior, severity, and tags. The public prompts are sanitized, so they test refusal and safe-completion behavior without exposing operational harmful instructions."

## 0:35-0:55 - New Eval Run

Open New Eval Run.

"I can select a suite, provider, model, and optional max case count. The mock provider runs without API keys, which makes the demo deterministic. The provider abstraction also supports OpenAI and Anthropic when keys are configured."

Run `jailbreak_basic` with `mock-safety-v1`.

## 0:55-1:20 - Dashboard and Scoring

Open the run dashboard.

"The dashboard summarizes pass rate, unsafe rate, average risk, refusal quality, failure rate by category, and severity distribution. The grader uses transparent heuristics: refusal phrases, safe alternatives, unsafe-intent indicators, and overcompliance signals."

## 1:20-1:35 - Human Review

Open an individual result.

"Automated grading is not the final word. A reviewer can mark a result as pass, review, or fail, add notes, and preserve the reviewed timestamp. That demonstrates a human-in-the-loop safety review workflow."

## 1:35-1:50 - Reports

Return to the dashboard and click Export Markdown Report.

"The report captures methodology, key metrics, category breakdown, high-risk findings, limitations, and recommendations. This is designed to look like a release-review artifact."

## 1:50-2:00 - Comparison

Open Compare Runs.

"Finally, model comparison helps identify regressions across model versions or providers by putting pass rate, unsafe rate, average risk, and category breakdown side by side."
