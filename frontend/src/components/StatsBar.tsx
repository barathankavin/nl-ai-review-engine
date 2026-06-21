import type { ReviewStats } from '../types/review';

interface StatsBarProps {
  stats: ReviewStats;
  filteredCount: number;
}

function DistributionBar({ stats }: { stats: ReviewStats }) {
  const max = Math.max(...Object.values(stats.distribution), 1);

  return (
    <div className="distribution">
      {[5, 4, 3, 2, 1].map((score) => {
        const count = stats.distribution[score] ?? 0;
        const width = `${(count / max) * 100}%`;

        return (
          <div key={score} className="distribution__row">
            <span className="distribution__label">{score}★</span>
            <div className="distribution__track">
              <div
                className={`distribution__fill distribution__fill--${score}`}
                style={{ width }}
              />
            </div>
            <span className="distribution__count">{count}</span>
          </div>
        );
      })}
    </div>
  );
}

export function StatsBar({ stats, filteredCount }: StatsBarProps) {
  const replyRate = stats.total ? Math.round((stats.withReply / stats.total) * 100) : 0;

  return (
    <section className="stats-bar">
      <article className="stat-card stat-card--hero">
        <p className="stat-card__label">Average rating</p>
        <p className="stat-card__value">{stats.averageScore.toFixed(1)}</p>
        <p className="stat-card__hint">Across {stats.total.toLocaleString()} scraped reviews</p>
      </article>

      <article className="stat-card">
        <p className="stat-card__label">Showing now</p>
        <p className="stat-card__value">{filteredCount.toLocaleString()}</p>
        <p className="stat-card__hint">After search & filters</p>
      </article>

      <article className="stat-card">
        <p className="stat-card__label">Developer replies</p>
        <p className="stat-card__value">{replyRate}%</p>
        <p className="stat-card__hint">{stats.withReply.toLocaleString()} reviews answered</p>
      </article>

      <article className="stat-card stat-card--wide">
        <p className="stat-card__label">Rating distribution</p>
        <DistributionBar stats={stats} />
      </article>
    </section>
  );
}
