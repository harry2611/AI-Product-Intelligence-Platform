import { FormEvent, useState } from 'react';
import { askAssistant } from '../api/client';
import { ChatResponse } from '../types';

export function ChatAssistant() {
  const [question, setQuestion] = useState('What are the top complaints this week?');
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await askAssistant(question);
      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <h2 className="text-lg font-semibold text-white">AI Product Manager Assistant</h2>
      <p className="mt-1 text-sm text-slate-400">RAG-powered Q&A over semantic feedback context.</p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-2">
        <input
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask product intelligence questions..."
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="w-fit rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-50"
        >
          {loading ? 'Thinking...' : 'Ask Assistant'}
        </button>
      </form>

      {result && (
        <div className="mt-4 space-y-3">
          <div className="rounded-lg border border-slate-700 bg-slate-950 p-3">
            <p className="whitespace-pre-wrap text-sm text-slate-100">{result.answer}</p>
          </div>

          <div>
            <h4 className="mb-2 text-sm font-semibold text-slate-300">Evidence</h4>
            <ul className="space-y-2">
              {result.citations.slice(0, 5).map((citation) => (
                <li key={`${citation.feedback_id}-${citation.score}`} className="rounded-md bg-slate-800/70 p-2 text-xs text-slate-300">
                  <p className="font-semibold text-slate-100">
                    Feedback #{citation.feedback_id} ({citation.source}) score={citation.score.toFixed(2)}
                  </p>
                  <p className="mt-1">{citation.message}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
