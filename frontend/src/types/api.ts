export interface Theme {
  id: string;
  label: string;
  description: string;
  sentiment_label: string;
  sentiment_score: number;
  review_count: number;
  volume_pct: number;
  avg_rating: number;
  trend: 'emerging' | 'declining' | 'stable' | 'spike' | string;
  severity_score: number;
  representative_quotes: Array<{ review_id: string; quote: string }>;
}

export interface ChatResponse {
  answer: string;
  citations: string[];
  intent: string;
  citations_valid: boolean;
  groq_enabled: boolean;
}

export interface ChatStatusResponse {
  groq_enabled: boolean;
  groq_model: string | null;
  sample_questions: string[];
}

export interface RefreshResponse {
  run_id: string;
  success: boolean;
  rows_ingested: number;
  new_clusters: number;
  themes_relabeled: number;
  groq_calls: number;
  latency_ms: number;
}

export interface HealthResponse {
  status: string;
  reviews: number;
  themes: number;
  groq_enabled?: boolean;
  groq_model?: string | null;
}
