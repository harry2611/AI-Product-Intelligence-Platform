interface RankedItem {
  key: string;
  value: number;
}

interface Props {
  title: string;
  items: RankedItem[];
}

export function RankedList({ title, items }: Props) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-200">{title}</h3>
      <ul className="space-y-2">
        {items.length === 0 && <li className="text-sm text-slate-400">No data yet</li>}
        {items.map((item) => (
          <li key={item.key} className="flex items-center justify-between rounded-md bg-slate-800/60 px-3 py-2 text-sm">
            <span className="text-slate-200">{item.key}</span>
            <span className="font-semibold text-white">{item.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
