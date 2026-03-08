import { triggerWeeklyReport } from '../api/client';
import { WeeklyReport } from '../types';

interface Props {
  report: WeeklyReport | null;
  onRefresh: () => void;
}

export function WeeklyReportPanel({ report, onRefresh }: Props) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Weekly AI Product Insight Report</h2>
          <p className="text-sm text-slate-400">Automated summary and recommendations.</p>
        </div>
        <button
          onClick={async () => {
            await triggerWeeklyReport();
            onRefresh();
          }}
          className="rounded-lg border border-slate-600 px-3 py-2 text-sm text-slate-100 hover:border-slate-400"
        >
          Generate Now
        </button>
      </div>

      {!report && <p className="mt-4 text-sm text-slate-400">No report generated yet.</p>}

      {report && (
        <div className="mt-4 space-y-4 text-sm">
          <p className="text-slate-300">
            Period: {new Date(report.period_start).toLocaleString()} - {new Date(report.period_end).toLocaleString()}
          </p>
          <pre className="overflow-auto rounded-lg border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200">
            {report.narrative}
          </pre>
        </div>
      )}
    </div>
  );
}
