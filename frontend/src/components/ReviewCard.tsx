import type { Review } from '../types/review';
import { formatRelativeDate, formatReviewDate } from '../lib/filters';
import { RatingStars } from './RatingStars';

interface ReviewCardProps {
  review: Review;
}

export function ReviewCard({ review }: ReviewCardProps) {
  const hasReply = Boolean(review.replyText.trim());

  return (
    <article className="review-card">
      <header className="review-card__header">
        <div className="review-card__author">
          {review.userImage ? (
            <img src={review.userImage} alt="" className="review-card__avatar" loading="lazy" />
          ) : (
            <div className="review-card__avatar review-card__avatar--fallback">
              {review.userName.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h3>{review.userName}</h3>
            <p>
              {formatReviewDate(review.date)}
              {review.date ? ` · ${formatRelativeDate(review.date)}` : ''}
            </p>
          </div>
        </div>

        <div className="review-card__meta">
          <RatingStars score={review.score} />
          {review.thumbsUp > 0 && (
            <span className="review-card__helpful">{review.thumbsUp} found helpful</span>
          )}
        </div>
      </header>

      {review.title && <p className="review-card__title">{review.title}</p>}
      <p className="review-card__text">{review.text || 'No review text provided.'}</p>

      <footer className="review-card__footer">
        <div className="review-card__tags">
          {review.version && <span className="tag">v{review.version}</span>}
          {hasReply && <span className="tag tag--accent">Developer replied</span>}
        </div>
        {review.url && (
          <a href={review.url} target="_blank" rel="noreferrer" className="review-card__link">
            View on Play Store
          </a>
        )}
      </footer>

      {hasReply && (
        <div className="review-card__reply">
          <p className="review-card__reply-label">
            Spotify response
            {review.replyDate ? ` · ${formatReviewDate(review.replyDate)}` : ''}
          </p>
          <p>{review.replyText}</p>
        </div>
      )}
    </article>
  );
}
