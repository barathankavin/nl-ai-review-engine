import { useCallback, useEffect, useMemo, useState } from 'react';
import { Header } from './components/Header';
import { StatsBar } from './components/StatsBar';
import { FilterPanel } from './components/FilterPanel';
import { ReviewList } from './components/ReviewList';
import { fetchReviews, getSheetMeta } from './lib/sheets';
import { computeStats, filterReviews } from './lib/filters';
import type { Review, ReviewFilters } from './types/review';
import './App.css';

const DEFAULT_FILTERS: ReviewFilters = {
  query: '',
  minScore: null,
  maxScore: null,
  hasReply: 'all',
  sort: 'newest',
};

export default function App() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [filters, setFilters] = useState<ReviewFilters>(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);

  const sheetMeta = getSheetMeta();

  const loadReviews = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchReviews();
      setReviews(data);
      setLastSynced(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load reviews');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadReviews();
  }, [loadReviews]);

  const filteredReviews = useMemo(
    () => filterReviews(reviews, filters),
    [reviews, filters],
  );

  const stats = useMemo(() => computeStats(reviews), [reviews]);

  return (
    <div className="app">
      <div className="app__backdrop" aria-hidden="true" />
      <Header
        sheetName={sheetMeta.sheetName}
        sourceLabel={sheetMeta.sourceLabel}
        lastSynced={lastSynced}
        loading={loading}
        onRefresh={() => void loadReviews()}
      />

      <main className="app__main">
        <StatsBar stats={stats} filteredCount={filteredReviews.length} />

        <div className="app__workspace">
          <FilterPanel filters={filters} onChange={setFilters} />
          <ReviewList
            reviews={filteredReviews}
            loading={loading}
            error={error}
            totalCount={reviews.length}
            onRetry={() => void loadReviews()}
          />
        </div>
      </main>
    </div>
  );
}
