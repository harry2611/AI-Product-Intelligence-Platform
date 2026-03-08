import { LiveEvent } from '../types';

interface Props {
  connected: boolean;
  events: LiveEvent[];
}

export function LiveEventFeed({ connected, events }: Props) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">Live Processing Stream</h3>
        <span className={`rounded-full px-2 py-1 text-xs ${connected ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
          {connected ? 'connected' : 'offline'}
        </span>
      </div>

      <ul className="max-h-64 space-y-2 overflow-auto">
        {events.length === 0 && <li className="text-xs text-slate-400">No events yet</li>}
        {events.map((event, idx) => (
          <li key={`${event.event}-${event.feedback_id ?? idx}-${idx}`} className="rounded-md bg-slate-800/60 p-2 text-xs text-slate-300">
            <p className="font-semibold text-slate-100">{event.event}</p>
            {event.feedback_id && <p>feedback_id: {event.feedback_id}</p>}
            {event.sentiment && <p>sentiment: {event.sentiment}</p>}
            {event.topics && <p>topics: {event.topics.join(', ')}</p>}
            {event.error && <p className="text-rose-300">error: {event.error}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}
