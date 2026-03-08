import axios from 'axios';
import {
  AnalyticsSummary,
  ChatResponse,
  FeatureRequestCountItem,
  TopicCountItem,
  TrendPoint,
  WeeklyReport,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
});

export async function submitManualFeedback(payload: {
  message: string;
  source: string;
  user_id: string;
}) {
  const { data } = await api.post('/feedback/manual', payload);
  return data;
}

export async function uploadFeedbackCSV(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/feedback/upload/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function uploadFeedbackJSON(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/feedback/upload/json', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function fetchSummary(days = 30): Promise<AnalyticsSummary> {
  const { data } = await api.get('/analytics/summary', { params: { days } });
  return data;
}

export async function fetchTrends(days = 30): Promise<TrendPoint[]> {
  const { data } = await api.get('/analytics/trends', { params: { days } });
  return data;
}

export async function fetchFeatureRequests(days = 30): Promise<FeatureRequestCountItem[]> {
  const { data } = await api.get('/analytics/feature-requests', { params: { days, limit: 10 } });
  return data;
}

export async function fetchTopComplaints(days = 30): Promise<TopicCountItem[]> {
  const { data } = await api.get('/analytics/top-complaints', { params: { days, limit: 10 } });
  return data;
}

export async function askAssistant(question: string): Promise<ChatResponse> {
  const { data } = await api.post('/assistant/query', { question, top_k: 8 });
  return data;
}

export async function fetchWeeklyReport(): Promise<WeeklyReport | null> {
  try {
    const { data } = await api.get('/reports/weekly/latest');
    return data;
  } catch {
    return null;
  }
}

export async function triggerWeeklyReport() {
  const { data } = await api.post('/reports/weekly/generate');
  return data;
}
