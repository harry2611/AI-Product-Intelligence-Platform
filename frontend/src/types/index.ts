export interface SentimentDistributionItem {
  label: string;
  count: number;
  percentage: number;
}

export interface TopicCountItem {
  topic: string;
  count: number;
}

export interface FeatureRequestCountItem {
  feature_name: string;
  count: number;
}

export interface AnalyticsSummary {
  total_feedback: number;
  processed_feedback: number;
  pending_feedback: number;
  sentiment_distribution: SentimentDistributionItem[];
  top_topics: TopicCountItem[];
  top_feature_requests: FeatureRequestCountItem[];
}

export interface TrendPoint {
  day: string;
  total_feedback: number;
  negative_feedback: number;
}

export interface ChatCitation {
  feedback_id: number;
  source: string;
  user_id: string;
  message: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  citations: ChatCitation[];
}

export interface WeeklyReport {
  id: number;
  period_start: string;
  period_end: string;
  top_issues: { topic: string; count: number }[];
  top_feature_requests: { feature_name: string; count: number }[];
  recommendations: string[];
  narrative: string;
  created_at: string;
}

export interface LiveEvent {
  event: string;
  feedback_id?: number;
  sentiment?: string;
  topics?: string[];
  source?: string;
  insight?: string;
  error?: string;
  report_id?: number;
  period_start?: string;
  period_end?: string;
}
