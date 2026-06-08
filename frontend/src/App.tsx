import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  FileText,
  FlaskConical,
  Home,
  Play,
  ShieldCheck,
  XCircle,
} from 'lucide-react';
import { FormEvent, ReactNode, useEffect, useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  compareEvalRuns,
  createEvalRun,
  getEvalRun,
  getEvalRunReportUrl,
  getEvalRunResults,
  getEvalRunSummary,
  getEvalSuite,
  getEvalSuites,
  getLegacyRuns,
  getProviders,
  getSummary,
  reviewEvalResult,
} from './api';
import type {
  EvalRunComparison,
  EvalResultDetail,
  EvalRunDetail,
  EvalRunScoreSummary,
  FileEvalSuite,
  FileEvalSuiteSummary,
  LegacyEvalRun,
  Provider,
  Summary,
} from './types';

type Route =
  | { page: 'home' }
  | { page: 'suites' }
  | { page: 'new-run' }
  | { page: 'compare' }
  | { page: 'run-dashboard'; runId: number }
  | { page: 'result-detail'; runId: number; resultId: number };

const percent = (value: number) => `${Math.round(value * 100)}%`;
const number = (value: number) => new Intl.NumberFormat().format(value);
const COLORS = {
  pass: '#0f766e',
  fail: '#b91c1c',
  safe: '#0f766e',
  borderline: '#b45309',
  unsafe: '#b91c1c',
  muted: '#94a3b8',
};

function App() {
  const [route, setRoute] = useState<Route>(() => parseRoute());

  useEffect(() => {
    const onHashChange = () => setRoute(parseRoute());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 text-ink">
      <AppShell route={route}>
        {route.page === 'home' ? <HomePage /> : null}
        {route.page === 'suites' ? <EvalSuitesPage /> : null}
        {route.page === 'new-run' ? <NewEvalRunPage /> : null}
        {route.page === 'compare' ? <CompareRunsPage /> : null}
        {route.page === 'run-dashboard' ? <RunDashboardPage runId={route.runId} /> : null}
        {route.page === 'result-detail' ? <ResultDetailPage runId={route.runId} resultId={route.resultId} /> : null}
      </AppShell>
    </div>
  );
}

function AppShell({ children, route }: { children: ReactNode; route: Route }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[248px_1fr]">
      <aside className="border-b border-slate-200 bg-white lg:border-b-0 lg:border-r">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 px-5 py-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-teal-700 text-white">
              <ShieldCheck size={22} />
            </div>
            <div>
              <div className="text-sm font-semibold uppercase text-teal-700">SafetyEval</div>
              <div className="text-lg font-semibold">Lab</div>
            </div>
          </div>
          <nav className="grid gap-1 px-3 pb-4 text-sm font-medium">
            <NavLink active={route.page === 'home'} href="#/" icon={<Home size={17} />} label="Home" />
            <NavLink
              active={route.page === 'suites'}
              href="#/suites"
              icon={<ClipboardList size={17} />}
              label="Eval Suites"
            />
            <NavLink
              active={route.page === 'new-run'}
              href="#/runs/new"
              icon={<Play size={17} />}
              label="New Eval Run"
            />
            <NavLink
              active={route.page === 'compare'}
              href="#/compare"
              icon={<BarChart3 size={17} />}
              label="Compare Runs"
            />
          </nav>
          <div className="mt-auto hidden border-t border-slate-200 p-4 text-xs leading-5 text-slate-500 lg:block">
            Internal safety review workspace for lightweight model-output evaluations.
          </div>
        </div>
      </aside>
      <main className="min-w-0">
        <header className="border-b border-slate-200 bg-white px-5 py-4">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase text-slate-500">Safety team console</div>
              <h1 className="text-2xl font-semibold text-ink">{pageTitle(route)}</h1>
            </div>
            <a
              className="inline-flex h-10 items-center gap-2 rounded-md bg-teal-700 px-3 text-sm font-semibold text-white hover:bg-teal-800"
              href="#/runs/new"
            >
              <Play size={17} />
              New run
            </a>
          </div>
        </header>
        <div className="mx-auto max-w-7xl px-5 py-6">{children}</div>
      </main>
    </div>
  );
}

function HomePage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [runs, setRuns] = useState<LegacyEvalRun[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getSummary(), getLegacyRuns()])
      .then(([nextSummary, nextRuns]) => {
        setSummary(nextSummary);
        setRuns(nextRuns);
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, []);

  const latestRun = runs[0];

  return (
    <div className="grid gap-5">
      {error ? <ErrorBanner message={error} /> : null}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<ClipboardList size={19} />} label="Suites" value={summary?.suite_count ?? 0} />
        <Metric icon={<FlaskConical size={19} />} label="Cases" value={summary?.case_count ?? 0} />
        <Metric icon={<BarChart3 size={19} />} label="Runs" value={summary?.run_count ?? 0} />
        <Metric label="Latest pass rate" value={percent(summary?.latest_pass_rate ?? 0)} />
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.5fr_1fr]">
        <Panel title="Recent eval runs" action={<a className="text-sm font-semibold text-teal-700" href="#/runs/new">Run a suite</a>}>
          <div className="overflow-hidden rounded-md border border-slate-200">
            <table className="w-full table-fixed text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-3">Run</th>
                  <th className="px-3 py-3">Model</th>
                  <th className="px-3 py-3">Pass rate</th>
                  <th className="px-3 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {runs.slice(0, 6).map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50">
                    <td className="px-3 py-3">
                      <a className="font-semibold text-teal-700" href={`#/runs/${run.id}`}>
                        Run {run.id}
                      </a>
                    </td>
                    <td className="truncate px-3 py-3 text-slate-600">{run.model_name}</td>
                    <td className="px-3 py-3">{percent(run.pass_rate)}</td>
                    <td className="px-3 py-3"><StatusBadge value={run.status} /></td>
                  </tr>
                ))}
                {runs.length === 0 ? (
                  <tr><td className="px-3 py-8 text-center text-slate-500" colSpan={4}>No runs yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Latest run">
          {latestRun ? (
            <div className="grid gap-4">
              <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Run {latestRun.id}</div>
                <div className="mt-1 text-3xl font-semibold">{percent(latestRun.pass_rate)}</div>
                <div className="mt-2 text-sm text-slate-600">
                  {latestRun.passed_cases}/{latestRun.total_cases} cases passed
                </div>
              </div>
              <a
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white text-sm font-semibold text-slate-700 hover:bg-slate-50"
                href={`#/runs/${latestRun.id}`}
              >
                Open dashboard
                <ArrowRight size={16} />
              </a>
            </div>
          ) : (
            <EmptyState title="No eval runs" body="Create a run to populate dashboard metrics." />
          )}
        </Panel>
      </section>
    </div>
  );
}

function EvalSuitesPage() {
  const [suites, setSuites] = useState<FileEvalSuiteSummary[]>([]);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [selectedSuite, setSelectedSuite] = useState<FileEvalSuite | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getEvalSuites()
      .then((nextSuites) => {
        setSuites(nextSuites);
        setSelectedName(nextSuites[0]?.name ?? null);
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, []);

  useEffect(() => {
    if (!selectedName) return;
    getEvalSuite(selectedName)
      .then(setSelectedSuite)
      .catch((loadError: Error) => setError(loadError.message));
  }, [selectedName]);

  return (
    <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
      {error ? <div className="lg:col-span-2"><ErrorBanner message={error} /></div> : null}
      <Panel title="Suites">
        <div className="grid gap-2">
          {suites.map((suite) => (
            <button
              className={`rounded-md border p-3 text-left transition ${
                selectedName === suite.name ? 'border-teal-600 bg-teal-50' : 'border-slate-200 bg-white hover:bg-slate-50'
              }`}
              key={suite.name}
              onClick={() => setSelectedName(suite.name)}
            >
              <div className="font-semibold">{suite.name}</div>
              <div className="mt-1 text-sm text-slate-600">{suite.case_count} cases</div>
            </button>
          ))}
        </div>
      </Panel>

      <Panel
        title={selectedSuite?.name ?? 'Suite detail'}
        action={
          selectedSuite ? (
            <a className="text-sm font-semibold text-teal-700" href={`#/runs/new?suite=${selectedSuite.name}`}>
              Run suite
            </a>
          ) : null
        }
      >
        {selectedSuite ? (
          <div className="grid gap-4">
            <div className="grid gap-3 md:grid-cols-3">
              <MiniStat label="Cases" value={selectedSuite.case_count} />
              <MiniStat label="Categories" value={selectedSuite.categories.length} />
              <MiniStat label="Severities" value={selectedSuite.severities.join(', ')} />
            </div>
            <div className="overflow-hidden rounded-md border border-slate-200">
              <table className="w-full table-fixed text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="w-44 px-3 py-3">Case</th>
                    <th className="px-3 py-3">Prompt</th>
                    <th className="w-32 px-3 py-3">Severity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {selectedSuite.cases.map((testCase) => (
                    <tr key={testCase.id}>
                      <td className="px-3 py-3 font-semibold">{testCase.id}</td>
                      <td className="px-3 py-3 text-slate-600">{testCase.prompt}</td>
                      <td className="px-3 py-3"><SeverityBadge value={testCase.severity} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState title="No suite selected" body="Select a suite to inspect cases." />
        )}
      </Panel>
    </div>
  );
}

function NewEvalRunPage() {
  const params = new URLSearchParams(window.location.hash.split('?')[1] ?? '');
  const preferredSuite = params.get('suite');
  const [suites, setSuites] = useState<FileEvalSuiteSummary[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [suiteName, setSuiteName] = useState(preferredSuite ?? '');
  const [providerName, setProviderName] = useState('mock');
  const [model, setModel] = useState('mock-safety-v1');
  const [maxCases, setMaxCases] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getEvalSuites(), getProviders()])
      .then(([nextSuites, nextProviders]) => {
        setSuites(nextSuites);
        setProviders(nextProviders);
        const initialSuite = preferredSuite ?? nextSuites[0]?.name ?? '';
        const initialProvider = nextProviders.find((provider) => provider.name === 'mock') ?? nextProviders[0];
        setSuiteName(initialSuite);
        setProviderName(initialProvider?.name ?? 'mock');
        setModel(initialProvider?.default_model ?? 'mock-safety-v1');
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, [preferredSuite]);

  function onProviderChange(value: string) {
    setProviderName(value);
    const provider = providers.find((item) => item.name === value);
    if (provider) setModel(provider.default_model);
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const run = await createEvalRun({
        suite_name: suiteName,
        provider: providerName,
        model,
        max_cases: maxCases ? Number(maxCases) : null,
      });
      window.location.hash = `#/runs/${run.run_id}`;
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Failed to create eval run');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <Panel title="Configure eval run">
        {error ? <ErrorBanner message={error} /> : null}
        <form className="mt-4 grid gap-5" onSubmit={onSubmit}>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Eval suite
            <select className="h-11 rounded-md border border-slate-300 bg-white px-3" value={suiteName} onChange={(event) => setSuiteName(event.target.value)}>
              {suites.map((suite) => (
                <option key={suite.name} value={suite.name}>{suite.name}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Provider
            <select className="h-11 rounded-md border border-slate-300 bg-white px-3" value={providerName} onChange={(event) => onProviderChange(event.target.value)}>
              {providers.map((provider) => (
                <option key={provider.name} value={provider.name}>
                  {provider.display_name}{provider.requires_api_key ? ' (API key)' : ''}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Model
            <input className="h-11 rounded-md border border-slate-300 bg-white px-3" value={model} onChange={(event) => setModel(event.target.value)} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Max cases
            <input className="h-11 rounded-md border border-slate-300 bg-white px-3" min="1" placeholder="All cases" type="number" value={maxCases} onChange={(event) => setMaxCases(event.target.value)} />
          </label>
          <button className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400" disabled={isSubmitting || !suiteName || !providerName}>
            <Play size={17} />
            {isSubmitting ? 'Running' : 'Run evaluation'}
          </button>
        </form>
      </Panel>
      <Panel title="Run policy">
        <div className="grid gap-4 text-sm text-slate-600">
          <MiniStat label="Execution" value="Synchronous" />
          <MiniStat label="Default provider" value="Mock, no API key" />
          <MiniStat label="Artifacts" value="EvalRun and EvalResult records" />
        </div>
      </Panel>
    </div>
  );
}

function CompareRunsPage() {
  const [runs, setRuns] = useState<LegacyEvalRun[]>([]);
  const [selectedRunIds, setSelectedRunIds] = useState<number[]>([]);
  const [comparison, setComparison] = useState<EvalRunComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isComparing, setIsComparing] = useState(false);

  useEffect(() => {
    getLegacyRuns()
      .then((nextRuns) => {
        setRuns(nextRuns);
        setSelectedRunIds(nextRuns.slice(0, 2).map((run) => run.id));
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, []);

  async function onCompare() {
    setError(null);
    setIsComparing(true);
    try {
      setComparison(await compareEvalRuns(selectedRunIds));
    } catch (compareError) {
      setError(compareError instanceof Error ? compareError.message : 'Failed to compare eval runs');
    } finally {
      setIsComparing(false);
    }
  }

  function toggleRun(runId: number) {
    setSelectedRunIds((current) =>
      current.includes(runId) ? current.filter((id) => id !== runId) : [...current, runId],
    );
  }

  const metricData = useMemo(() => {
    if (!comparison) return [];
    return comparison.runs.map((run) => ({
      name: `Run ${run.run_id}`,
      passRate: run.pass_rate,
      unsafeRate: run.unsafe_rate,
      averageRisk: run.average_risk_score,
    }));
  }, [comparison]);

  const categoryData = useMemo(() => {
    if (!comparison) return [];
    return comparison.category_breakdown.map((item) => ({
      category: item.category,
      ...Object.fromEntries(Object.entries(item.failure_rates).map(([runId, rate]) => [`Run ${runId}`, rate])),
    }));
  }, [comparison]);

  return (
    <div className="grid gap-5">
      {error ? <ErrorBanner message={error} /> : null}
      <Panel title="Select eval runs" action={<span className="text-sm text-slate-500">{selectedRunIds.length} selected</span>}>
        <div className="grid gap-4 lg:grid-cols-[1fr_180px]">
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            {runs.map((run) => (
              <label
                className={`flex cursor-pointer gap-3 rounded-md border p-3 ${
                  selectedRunIds.includes(run.id) ? 'border-teal-600 bg-teal-50' : 'border-slate-200 bg-white hover:bg-slate-50'
                }`}
                key={run.id}
              >
                <input
                  checked={selectedRunIds.includes(run.id)}
                  className="mt-1"
                  onChange={() => toggleRun(run.id)}
                  type="checkbox"
                />
                <span>
                  <span className="block font-semibold">Run {run.id}</span>
                  <span className="block text-sm text-slate-600">{run.model_name}</span>
                  <span className="mt-1 block text-xs text-slate-500">{percent(run.pass_rate)} pass · {run.total_cases} cases</span>
                </span>
              </label>
            ))}
          </div>
          <button
            className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400"
            disabled={selectedRunIds.length < 2 || isComparing}
            onClick={onCompare}
          >
            <BarChart3 size={17} />
            {isComparing ? 'Comparing' : 'Compare'}
          </button>
        </div>
      </Panel>

      {comparison ? (
        <>
          <section className="grid gap-5 xl:grid-cols-2">
            <Panel title="Pass and unsafe rates">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metricData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis tickFormatter={percent} />
                    <Tooltip formatter={(value: number) => (value <= 1 ? percent(value) : value)} />
                    <Legend />
                    <Bar dataKey="passRate" fill={COLORS.pass} name="Pass rate" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="unsafeRate" fill={COLORS.fail} name="Unsafe rate" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>
            <Panel title="Average risk score">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metricData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="averageRisk" fill="#475569" name="Average risk" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>
          </section>

          <Panel title="Category breakdown">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="category" />
                  <YAxis tickFormatter={percent} />
                  <Tooltip formatter={(value: number) => percent(value)} />
                  <Legend />
                  {comparison.runs.map((run, index) => (
                    <Bar
                      dataKey={`Run ${run.run_id}`}
                      fill={['#0f766e', '#b45309', '#334155', '#b91c1c'][index % 4]}
                      key={run.run_id}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Panel>

          <Panel title="Side-by-side metrics">
            <div className="overflow-hidden rounded-md border border-slate-200">
              <table className="w-full table-fixed text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-3">Run</th>
                    <th className="px-3 py-3">Model</th>
                    <th className="px-3 py-3">Suite</th>
                    <th className="px-3 py-3">Pass rate</th>
                    <th className="px-3 py-3">Unsafe rate</th>
                    <th className="px-3 py-3">Avg risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {comparison.runs.map((run) => (
                    <tr key={run.run_id}>
                      <td className="px-3 py-3">
                        <a className="font-semibold text-teal-700" href={`#/runs/${run.run_id}`}>Run {run.run_id}</a>
                      </td>
                      <td className="truncate px-3 py-3 text-slate-600">{run.model}</td>
                      <td className="truncate px-3 py-3 text-slate-600">{run.suite_name}</td>
                      <td className="px-3 py-3">{percent(run.pass_rate)}</td>
                      <td className="px-3 py-3">{percent(run.unsafe_rate)}</td>
                      <td className="px-3 py-3">{run.average_risk_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      ) : (
        <EmptyState title="No comparison yet" body="Select two or more completed runs to benchmark model behavior." />
      )}
    </div>
  );
}

function RunDashboardPage({ runId }: { runId: number }) {
  const [detail, setDetail] = useState<EvalRunDetail | null>(null);
  const [summary, setSummary] = useState<EvalRunScoreSummary | null>(null);
  const [results, setResults] = useState<EvalResultDetail[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getEvalRun(runId), getEvalRunSummary(runId), getEvalRunResults(runId)])
      .then(([nextDetail, nextSummary, nextResults]) => {
        setDetail(nextDetail);
        setSummary(nextSummary);
        setResults(nextResults);
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, [runId]);

  const passFailData = useMemo(
    () => [
      { name: 'Passed', value: detail?.passed_cases ?? 0, color: COLORS.pass },
      { name: 'Failed', value: detail?.failed_cases ?? 0, color: COLORS.fail },
    ],
    [detail],
  );
  const categoryData = useMemo(
    () =>
      Object.entries(summary?.failure_rate_by_category ?? {}).map(([category, rate]) => ({
        category,
        rate,
      })),
    [summary],
  );
  const severityData = useMemo(() => {
    const counts = results.reduce<Record<string, number>>((acc, result) => {
      acc[result.severity] = (acc[result.severity] ?? 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([severity, count]) => ({ severity, count }));
  }, [results]);
  const notableResults = results.filter((result) => result.verdict === 'fail' || result.safety_label === 'borderline');
  const reviewedCount = results.filter((result) => result.review_status !== 'unreviewed').length;
  const unreviewedCount = results.length - reviewedCount;

  if (error) return <ErrorBanner message={error} />;
  if (!detail || !summary) return <LoadingState />;

  return (
    <div className="grid gap-5">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric label="Pass rate" value={percent(summary.pass_rate)} icon={<CheckCircle2 size={19} />} />
        <Metric label="Unsafe rate" value={percent(summary.unsafe_rate)} icon={<XCircle size={19} />} />
        <Metric label="Avg risk" value={summary.average_risk_score} icon={<AlertTriangle size={19} />} />
        <Metric label="Refusal quality" value={summary.refusal_quality_score} icon={<ShieldCheck size={19} />} />
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        <Metric label="Reviewed results" value={reviewedCount} icon={<CheckCircle2 size={19} />} />
        <Metric label="Unreviewed results" value={unreviewedCount} icon={<FileText size={19} />} />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <Panel title="Pass/fail">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={passFailData} dataKey="value" innerRadius={65} outerRadius={94} paddingAngle={3}>
                  {passFailData.map((entry) => <Cell fill={entry.color} key={entry.name} />)}
                </Pie>
                <Tooltip formatter={(value: number) => number(value)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Failure rate by category">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="category" />
                <YAxis tickFormatter={percent} />
                <Tooltip formatter={(value: number) => percent(value)} />
                <Bar dataKey="rate" fill={COLORS.fail} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Severity distribution">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="severity" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#475569" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>

        <Panel
        title="Failed and borderline cases"
        action={
          <a
            className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            href={getEvalRunReportUrl(runId)}
          >
            <FileText size={16} />
            Export Markdown Report
          </a>
        }
      >
        <ResultTable results={notableResults} runId={runId} />
      </Panel>
    </div>
  );
}

function ResultDetailPage({ runId, resultId }: { runId: number; resultId: number }) {
  const [result, setResult] = useState<EvalResultDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reviewStatus, setReviewStatus] = useState<'pass' | 'review' | 'fail'>('review');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [isSavingReview, setIsSavingReview] = useState(false);

  useEffect(() => {
    getEvalRunResults(runId)
      .then((results) => {
        const nextResult = results.find((item) => item.result_id === resultId);
        if (!nextResult) throw new Error('Result not found');
        setResult(nextResult);
        if (nextResult.review_status !== 'unreviewed') setReviewStatus(nextResult.review_status);
        setReviewerNotes(nextResult.reviewer_notes);
      })
      .catch((loadError: Error) => setError(loadError.message));
  }, [runId, resultId]);

  if (error) return <ErrorBanner message={error} />;
  if (!result) return <LoadingState />;

  async function saveReview(event: FormEvent) {
    event.preventDefault();
    if (!result) return;
    setIsSavingReview(true);
    setError(null);
    try {
      const review = await reviewEvalResult(result.result_id, {
        review_status: reviewStatus,
        reviewer_notes: reviewerNotes,
      });
      setResult({
        ...result,
        review_status: review.review_status,
        reviewer_notes: review.reviewer_notes,
        reviewed_at: review.reviewed_at,
      });
    } catch (reviewError) {
      setError(reviewError instanceof Error ? reviewError.message : 'Failed to save review');
    } finally {
      setIsSavingReview(false);
    }
  }

  return (
    <div className="grid gap-5">
      <a className="inline-flex items-center gap-2 text-sm font-semibold text-teal-700" href={`#/runs/${runId}`}>
        <ArrowRight className="rotate-180" size={16} />
        Back to dashboard
      </a>
      <section className="grid gap-4 md:grid-cols-4">
        <Metric label="Verdict" value={result.verdict} />
        <Metric label="Safety label" value={result.safety_label} />
        <Metric label="Risk score" value={result.risk_score} />
        <Metric label="Severity" value={result.severity} />
      </section>
      <Panel title="Human review" action={<ReviewBadge value={result.review_status} />}>
        <form className="grid gap-4" onSubmit={saveReview}>
          <div className="grid gap-3 sm:grid-cols-3">
            {(['pass', 'review', 'fail'] as const).map((status) => (
              <label
                className={`flex cursor-pointer items-center justify-center rounded-md border px-3 py-3 text-sm font-semibold capitalize ${
                  reviewStatus === status ? 'border-teal-600 bg-teal-50 text-teal-800' : 'border-slate-200 bg-white text-slate-700'
                }`}
                key={status}
              >
                <input
                  checked={reviewStatus === status}
                  className="sr-only"
                  name="review-status"
                  onChange={() => setReviewStatus(status)}
                  type="radio"
                />
                {status}
              </label>
            ))}
          </div>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Reviewer notes
            <textarea
              className="min-h-28 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6"
              onChange={(event) => setReviewerNotes(event.target.value)}
              placeholder="Add context, adjudication notes, or follow-up actions."
              value={reviewerNotes}
            />
          </label>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-slate-500">
              {result.reviewed_at ? `Reviewed at ${result.reviewed_at}` : 'No human review recorded yet.'}
            </div>
            <button
              className="inline-flex h-10 items-center justify-center rounded-md bg-teal-700 px-4 text-sm font-semibold text-white hover:bg-teal-800 disabled:bg-slate-400"
              disabled={isSavingReview}
            >
              {isSavingReview ? 'Saving' : 'Save review'}
            </button>
          </div>
        </form>
      </Panel>
      <Panel title={result.case_title} action={<SeverityBadge value={result.severity} />}>
        <div className="grid gap-5 lg:grid-cols-2">
          <TextBlock label="Prompt" value={result.prompt} />
          <TextBlock label="Model response" value={result.model_response} />
          <TextBlock label="Expected behavior" value={result.expected_behavior} />
          <TextBlock label="Rationale" value={result.rationale} />
        </div>
      </Panel>
    </div>
  );
}

function ResultTable({ results, runId }: { results: EvalResultDetail[]; runId: number }) {
  if (results.length === 0) return <EmptyState title="No failed or borderline cases" body="This run has no review queue items." />;

  return (
    <div className="overflow-hidden rounded-md border border-slate-200">
      <table className="w-full table-fixed text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="w-44 px-3 py-3">Case</th>
            <th className="w-32 px-3 py-3">Label</th>
            <th className="w-28 px-3 py-3">Risk</th>
            <th className="w-32 px-3 py-3">Review</th>
            <th className="px-3 py-3">Category</th>
            <th className="w-28 px-3 py-3">Detail</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {results.map((result) => (
            <tr key={result.result_id} className="hover:bg-slate-50">
              <td className="px-3 py-3 font-semibold">{result.case_title}</td>
              <td className="px-3 py-3"><SafetyLabelBadge value={result.safety_label} /></td>
              <td className="px-3 py-3">{result.risk_score}</td>
              <td className="px-3 py-3"><ReviewBadge value={result.review_status} /></td>
              <td className="px-3 py-3 text-slate-600">{result.category}</td>
              <td className="px-3 py-3">
                <a className="font-semibold text-teal-700" href={`#/runs/${runId}/results/${result.result_id}`}>Open</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Metric({ icon, label, value }: { icon?: ReactNode; label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between text-slate-500">
        <span className="text-sm font-medium">{label}</span>
        {icon}
      </div>
      <div className="mt-3 truncate text-3xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <div className="text-xs font-semibold uppercase text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-800">{value}</div>
    </div>
  );
}

function Panel({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h2 className="text-lg font-semibold text-ink">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function TextBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
      <div className="mb-2 text-xs font-semibold uppercase text-slate-500">{label}</div>
      <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{value}</p>
    </div>
  );
}

function NavLink({ active, href, icon, label }: { active: boolean; href: string; icon: ReactNode; label: string }) {
  return (
    <a
      className={`flex h-10 items-center gap-3 rounded-md px-3 ${
        active ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      }`}
      href={href}
    >
      {icon}
      {label}
    </a>
  );
}

function StatusBadge({ value }: { value: string }) {
  return <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold capitalize text-slate-700">{value}</span>;
}

function SeverityBadge({ value }: { value: string }) {
  const color = value === 'critical' || value === 'high' ? 'bg-red-50 text-red-700' : value === 'medium' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-700';
  return <span className={`rounded px-2 py-1 text-xs font-semibold capitalize ${color}`}>{value}</span>;
}

function SafetyLabelBadge({ value }: { value: string }) {
  const color = value === 'unsafe' ? 'bg-red-50 text-red-700' : value === 'borderline' ? 'bg-amber-50 text-amber-700' : 'bg-teal-50 text-teal-700';
  return <span className={`rounded px-2 py-1 text-xs font-semibold capitalize ${color}`}>{value}</span>;
}

function ReviewBadge({ value }: { value: string }) {
  const color = value === 'fail'
    ? 'bg-red-50 text-red-700'
    : value === 'review'
      ? 'bg-amber-50 text-amber-700'
      : value === 'pass'
        ? 'bg-teal-50 text-teal-700'
        : 'bg-slate-100 text-slate-600';
  return <span className={`rounded px-2 py-1 text-xs font-semibold capitalize ${color}`}>{value}</span>;
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {message}
    </div>
  );
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center">
      <FileText className="mx-auto text-slate-400" size={28} />
      <div className="mt-3 font-semibold">{title}</div>
      <div className="mt-1 text-sm text-slate-500">{body}</div>
    </div>
  );
}

function LoadingState() {
  return <div className="rounded-md border border-slate-200 bg-white p-6 text-sm text-slate-500">Loading...</div>;
}

function parseRoute(): Route {
  const hash = window.location.hash.replace(/^#/, '') || '/';
  const path = hash.split('?')[0];
  const resultMatch = path.match(/^\/runs\/(\d+)\/results\/(\d+)$/);
  if (resultMatch) return { page: 'result-detail', runId: Number(resultMatch[1]), resultId: Number(resultMatch[2]) };
  const runMatch = path.match(/^\/runs\/(\d+)$/);
  if (runMatch) return { page: 'run-dashboard', runId: Number(runMatch[1]) };
  if (path === '/suites') return { page: 'suites' };
  if (path === '/runs/new') return { page: 'new-run' };
  if (path === '/compare') return { page: 'compare' };
  return { page: 'home' };
}

function pageTitle(route: Route) {
  if (route.page === 'suites') return 'Eval Suites';
  if (route.page === 'new-run') return 'New Eval Run';
  if (route.page === 'compare') return 'Compare Runs';
  if (route.page === 'run-dashboard') return `Run Dashboard ${route.runId}`;
  if (route.page === 'result-detail') return `Result Detail ${route.resultId}`;
  return 'Home';
}

export default App;
