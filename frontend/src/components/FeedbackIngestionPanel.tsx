import { FormEvent, useState } from 'react';
import { submitManualFeedback, uploadFeedbackCSV, uploadFeedbackJSON } from '../api/client';

interface Props {
  onSuccess: () => void;
}

export function FeedbackIngestionPanel({ onSuccess }: Props) {
  const [message, setMessage] = useState('');
  const [source, setSource] = useState('manual');
  const [userId, setUserId] = useState('pm_dashboard');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      await submitManualFeedback({ message, source, user_id: userId });
      setMessage('');
      setStatus('Feedback queued successfully');
      onSuccess();
    } catch {
      setStatus('Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(file: File) {
    setLoading(true);
    setStatus(null);
    try {
      if (file.name.endsWith('.csv')) {
        await uploadFeedbackCSV(file);
      } else if (file.name.endsWith('.json')) {
        await uploadFeedbackJSON(file);
      } else {
        setStatus('Use CSV or JSON files only');
        return;
      }
      setStatus('File uploaded and queued for processing');
      onSuccess();
    } catch {
      setStatus('File upload failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <h2 className="text-lg font-semibold text-white">Feedback Ingestion</h2>
      <p className="mt-1 text-sm text-slate-400">Manual input, CSV upload, JSON upload, or API ingest.</p>

      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <textarea
          className="h-28 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand-400"
          placeholder="Paste product feedback here..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          required
        />

        <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            placeholder="source (manual/slack/app-store)"
          />
          <input
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
            placeholder="user_id"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-400 disabled:opacity-50"
          >
            {loading ? 'Queueing...' : 'Submit Feedback'}
          </button>

          <label className="cursor-pointer rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-slate-500">
            Upload CSV/JSON
            <input
              type="file"
              accept=".csv,.json"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) handleFileUpload(file);
              }}
            />
          </label>
        </div>
      </form>

      {status && <p className="mt-3 text-sm text-slate-300">{status}</p>}
    </div>
  );
}
