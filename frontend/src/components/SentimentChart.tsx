import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { SentimentDistributionItem } from '../types';

interface Props {
  data: SentimentDistributionItem[];
}

const colors: Record<string, string> = {
  Positive: '#34d399',
  Neutral: '#fbbf24',
  Negative: '#fb7185',
};

export function SentimentChart({ data }: Props) {
  return (
    <div className="h-72 rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-200">Sentiment Distribution</h3>
      <ResponsiveContainer width="100%" height="88%">
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="label" outerRadius={95} label>
            {data.map((item) => (
              <Cell key={item.label} fill={colors[item.label] ?? '#60a5fa'} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
