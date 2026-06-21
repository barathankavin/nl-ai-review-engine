import type { Review } from '../types/review';
import { ReviewCard } from './ReviewCard';

interface ReviewListProps {
  reviews: Review[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  onRetry: () => void;
}

export function ReviewList({
  reviews,
  loading,
  error,
  totalCount,
  onRetry,
}: ReviewListProps) {
  if (loading && reviews.length === 0) {
    return (
      <section className="review-list">
        <div className="empty-state">
          <div className="spinner" aria-hidden="true" />
          <p>Loading reviews from Google Sheets…</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="review-list">
        <div className="empty-state empty-state--error">
          <h2>Could not load reviews</h2>
          <p>{error}</p>
          <button type="button" className="button button--primary" onClick={onRetry}>
            Try again
          </button>
        </div>
      </section>
    );
  }

  if (reviews.length === 0) {
    return (
      <section className="review-list">
        <div className="empty-state">
          <h2>No reviews match your filters</h2>
          <p>
            {totalCount > 0
              ? 'Try clearing filters or broadening your search.'
              : 'Run the n8n workflow to scrape reviews into the sheet, then refresh.'}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="review-list">
      <div className="review-list__header">
        <h2>Discovered reviews</h2>
        <p>{reviews.length.toLocaleString()} results</p>
      </div>
      <div className="review-list__grid">
        {reviews.map((review) => (
          <ReviewCard key={review.id || `${review.userName}-${review.date}`} review={review} />
        ))}
      </div>
    </section>
  );
}
