import type { ChatResponse, ChatStatusResponse, HealthResponse, RefreshResponse, Theme } from '../types/api';
import type { Review } from '../types/review';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export function fetchHealth() {
  return request<HealthResponse>('/health');
}

export function fetchThemes() {
  return request<Theme[]>('/themes');
}

export function fetchThemeReviews(themeId: string) {
  return request<{ theme: { id: string; label: string; description: string }; reviews: Review[] }>(
    `/themes/${themeId}/reviews`,
  );
}

export function fetchBackendReviews() {
  return request<Review[]>('/reviews');
}

export function runPipelineRefresh() {
  return request<RefreshResponse>('/refresh', { method: 'POST' });
}

export function fetchChatStatus() {
  return request<ChatStatusResponse>('/chat/status');
}

export function sendChatQuery(query: string) {
  return request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}
