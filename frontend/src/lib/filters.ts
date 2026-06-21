import type { Review, ReviewFilters, ReviewStats } from '../types/review';

export function computeStats(reviews: Review[]): ReviewStats {
  const distribution: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  let scoreSum = 0;
  let withReply = 0;

  for (const review of reviews) {
    const score = Math.min(5, Math.max(1, Math.round(review.score))) as 1 | 2 | 3 | 4 | 5;
    distribution[score] += 1;
    scoreSum += review.score;
    if (review.replyText.trim()) withReply += 1;
  }

  return {
    total: reviews.length,
    averageScore: reviews.length ? scoreSum / reviews.length : 0,
    withReply,
    distribution,
  };
}

function matchesQuery(review: Review, query: string): boolean {
  if (!query.trim()) return true;
  const haystack = [
    review.userName,
    review.title,
    review.text,
    review.replyText,
    review.version,
  ]
    .join(' ')
    .toLowerCase();
  return haystack.includes(query.trim().toLowerCase());
}

function matchesScore(review: Review, min: number | null, max: number | null): boolean {
  if (min !== null && review.score < min) return false;
  if (max !== null && review.score > max) return false;
  return true;
}

function matchesReply(review: Review, hasReply: ReviewFilters['hasReply']): boolean {
  if (hasReply === 'all') return true;
  const replied = Boolean(review.replyText.trim());
  return hasReply === 'yes' ? replied : !replied;
}

function sortReviews(reviews: Review[], sort: ReviewFilters['sort']): Review[] {
  const sorted = [...reviews];

  switch (sort) {
    case 'oldest':
      return sorted.sort((a, b) => a.date.localeCompare(b.date));
    case 'rating-high':
      return sorted.sort((a, b) => b.score - a.score || b.date.localeCompare(a.date));
    case 'rating-low':
      return sorted.sort((a, b) => a.score - b.score || b.date.localeCompare(a.date));
    case 'helpful':
      return sorted.sort((a, b) => b.thumbsUp - a.thumbsUp || b.date.localeCompare(a.date));
    case 'newest':
    default:
      return sorted.sort((a, b) => b.date.localeCompare(a.date));
  }
}

export function filterReviews(reviews: Review[], filters: ReviewFilters): Review[] {
  const filtered = reviews.filter(
    (review) =>
      matchesQuery(review, filters.query) &&
      matchesScore(review, filters.minScore, filters.maxScore) &&
      matchesReply(review, filters.hasReply),
  );

  return sortReviews(filtered, filters.sort);
}

export function formatReviewDate(value: string): string {
  if (!value) return 'Unknown date';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

export function formatRelativeDate(value: string): string {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';

  const diffMs = Date.now() - date.getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (days <= 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 30) return `${days}d ago`;
  if (days < 365) return `${Math.floor(days / 30)}mo ago`;
  return `${Math.floor(days / 365)}y ago`;
}
