import type { Theme } from '../types/api';
import type { Review } from '../types/review';
import { DonutChart } from './DonutChart';
import { ReviewCard } from './ReviewCard';

interface PatternDashboardProps {
  themes: Theme[];
  loading: boolean;
  selectedThemeId: string | null;
  selectedTheme: Theme | null;
  patternReviews: Review[];
  reviewsLoading: boolean;
  onSelectTheme: (themeId: string | null) => void;
}

const TREND_LABELS: Record<string, string> = {
  emerging: 'Trending up',
  declining: 'Declining',
  stable: 'Stable',
  spike: 'Spike',
};

export function PatternDashboard({
  themes,
  loading,
  selectedThemeId,
  selectedTheme,
  patternReviews,
  reviewsLoading,
  onSelectTheme,
}: PatternDashboardProps) {
  if (loading) {
    return (
      <section className="pattern-dashboard">
        <div className="empty-state">
          <div className="spinner" aria-hidden="true" />
          <p>Loading patterns…</p>
        </div>
      </section>
    );
  }

  if (themes.length === 0) {
    return (
      <section className="pattern-dashboard">
        <div className="empty-state">
          <h2>No patterns yet</h2>
          <p>Run pipeline refresh to cluster reviews into observed patterns.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="pattern-dashboard">
      <div className="pattern-dashboard__header">
        <div>
          <h2 className="section-title">Patterns observed</h2>
          <p className="section-subtitle">
            {themes.length} signals from {themes.reduce((n, t) => n + t.review_count, 0)} reviews
          </p>
        </div>
      </div>

      <div className="pattern-dashboard__overview">
        <DonutChart themes={themes} />
      </div>

      <div className="pattern-dashboard__grid">
        {themes.map((theme) => {
          const active = selectedThemeId === theme.id;
          return (
            <button
              key={theme.id}
              type="button"
              className={`pattern-card ${active ? 'pattern-card--active' : ''}`}
              onClick={() => onSelectTheme(active ? null : theme.id)}
            >
              <div className="pattern-card__accent" aria-hidden="true" />
              <div className="pattern-card__top">
                <h3>{theme.label}</h3>
                <span className={`trend trend--${theme.trend}`}>
                  {TREND_LABELS[theme.trend] ?? theme.trend}
                </span>
              </div>
              <p>{theme.description}</p>
              <div className="pattern-card__stats">
                <span className="pattern-card__stat">
                  <strong>{theme.review_count}</strong> reviews
                </span>
                <span>{theme.volume_pct.toFixed(1)}% share</span>
                <span>{theme.sentiment_label}</span>
              </div>
              <div className="pattern-card__bar">
                <div className="pattern-card__bar-fill" style={{ width: `${Math.min(theme.volume_pct * 2, 100)}%` }} />
              </div>
            </button>
          );
        })}
      </div>

      {selectedTheme && (
        <div className="pattern-detail">
          <div className="pattern-detail__header">
            <div>
              <p className="pattern-detail__eyebrow">Selected pattern</p>
              <h3>{selectedTheme.label}</h3>
              <p>{selectedTheme.description}</p>
            </div>
            <div className="pattern-detail__meta">
              <span className="pattern-detail__badge">{selectedTheme.review_count} reviews</span>
              <span className={`trend trend--${selectedTheme.trend}`}>
                {TREND_LABELS[selectedTheme.trend] ?? selectedTheme.trend}
              </span>
            </div>
          </div>

          {reviewsLoading ? (
            <div className="empty-state empty-state--compact">
              <div className="spinner" aria-hidden="true" />
              <p>Loading all reviews for this pattern…</p>
            </div>
          ) : patternReviews.length === 0 ? (
            <div className="empty-state empty-state--compact">
              <p>No reviews found for this pattern.</p>
            </div>
          ) : (
            <>
              <p className="pattern-detail__count">
                Showing all <strong>{patternReviews.length}</strong> reviews in this pattern
              </p>
              <div className="pattern-detail__reviews">
                {patternReviews.map((review) => (
                  <ReviewCard key={review.id} review={review} />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </section>
  );
}
