import { useEffect, useState } from 'react';
import {
  fetchFeatureRequests,
  fetchSummary,
  fetchTopComplaints,
  fetchTrends,
  fetchWeeklyReport,
} from '../api/client';
import { ChatAssistant } from '../components/ChatAssistant';
import { FeedbackIngestionPanel } from '../components/FeedbackIngestionPanel';
import { LiveEventFeed } from '../components/LiveEventFeed';
import { MetricCard } from '../components/MetricCard';
import { RankedList } from '../components/RankedList';
import { SentimentChart } from '../components/SentimentChart';
import { TrendChart } from '../components/TrendChart';
import { WeeklyReportPanel } from '../components/WeeklyReportPanel';
import { useLiveUpdates } from '../hooks/useLiveUpdates';
import {
  AnalyticsSummary,
  FeatureRequestCountItem,
  TopicCountItem,
  TrendPoint,
  WeeklyReport,
} from '../types';

export function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [featureRequests, setFeatureRequests] = useState<FeatureRequestCountItem[]>([]);
  const [complaints, setComplaints] = useState<TopicCountItem[]>([]);
  const [report, setReport] = useState<WeeklyReport | null>(null);

  const { connected, events, latestEvent } = useLiveUpdates();

  async function refreshAll() {
    const [summaryData, trendData, featuresData, complaintsData, reportData] = await Promise.all([
      fetchSummary(30),
      fetchTrends(30),
      fetchFeatureRequests(30),
      fetchTopComplaints(30),
      fetchWeeklyReport(),
    ]);
    setSummary(summaryData);
    setTrends(trendData);
    setFeatureRequests(featuresData);
    setComplaints(complaintsData);
    setReport(reportData);
  }

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    if (latestEvent?.event === 'feedback_processed' || latestEvent?.event === 'weekly_report_generated') {
      refreshAll();
    }
  }, [latestEvent]);

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-4 md:p-8">
      <header className="rounded-2xl border border-slate-800 bg-gradient-to-br from-brand-700/40 to-slate-900 p-6">
        <h1 className="text-3xl font-bold text-white">AI Product Intelligence Platform</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-200">
          LLM pipelines + RAG + Chroma semantic retrieval + queue workers + live analytics for product teams.
        </p>
      </header>

      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard label="Total Feedback" value={summary?.total_feedback ?? 0} accent="sky" />
        <MetricCard label="Processed" value={summary?.processed_feedback ?? 0} accent="emerald" />
        <MetricCard label="Pending" value={summary?.pending_feedback ?? 0} accent="amber" />
        <MetricCard
          label="Negative %"
          value={Math.round(summary?.sentiment_distribution.find((s) => s.label === 'Negative')?.percentage ?? 0)}
          accent="rose"
        />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <FeedbackIngestionPanel onSuccess={refreshAll} />
        <ChatAssistant />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <SentimentChart data={summary?.sentiment_distribution ?? []} />
        <TrendChart data={trends} />
        <LiveEventFeed connected={connected} events={events} />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <RankedList
          title="Top Topics"
          items={(summary?.top_topics ?? []).map((item) => ({ key: item.topic, value: item.count }))}
        />
        <RankedList
          title="Feature Request Frequency"
          items={featureRequests.map((item) => ({ key: item.feature_name, value: item.count }))}
        />
        <RankedList
          title="Top Complaints"
          items={complaints.map((item) => ({ key: item.topic, value: item.count }))}
        />
      </section>

      <section>
        <WeeklyReportPanel report={report} onRefresh={refreshAll} />
      </section>
    </div>
  );
}
