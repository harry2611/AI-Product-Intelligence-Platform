interface MetricCardProps {
  label: string;
  value: number;
  accent?: 'emerald' | 'amber' | 'rose' | 'sky';
}

const accents = {
  emerald: 'from-emerald-500/25 to-emerald-500/5 border-emerald-500/40',
  amber: 'from-amber-500/25 to-amber-500/5 border-amber-500/40',
  rose: 'from-rose-500/25 to-rose-500/5 border-rose-500/40',
  sky: 'from-sky-500/25 to-sky-500/5 border-sky-500/40',
};

export function MetricCard({ label, value, accent = 'sky' }: MetricCardProps) {
  return (
    <div className={`rounded-xl border bg-gradient-to-br p-4 shadow-lg ${accents[accent]}`}>
      <p className="text-xs uppercase tracking-wide text-slate-300">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
}
