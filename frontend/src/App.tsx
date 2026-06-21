import { useCallback, useEffect, useMemo, useState } from 'react';
import { Header } from './components/Header';
import { StatsBar } from './components/StatsBar';
import { FilterPanel } from './components/FilterPanel';
import { ReviewList } from './components/ReviewList';
import { PatternDashboard } from './components/PatternDashboard';
import { ChatPanel } from './components/ChatPanel';
import {
  fetchBackendReviews,
  fetchHealth,
  fetchThemeReviews,
  fetchThemes,
  runPipelineRefresh,
} from './lib/api';
import { fetchReviews, getSheetMeta } from './lib/sheets';
import { computeStats, filterReviews } from './lib/filters';
import type { Theme } from './types/api';
import type { Review, ReviewFilters } from './types/review';
import './App.css';

const DEFAULT_FILTERS: ReviewFilters = {
  query: '',
  minScore: null,
  maxScore: null,
  hasReply: 'all',
  sort: 'newest',
};

type ViewMode = 'patterns' | 'discovery';

export default function App() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [patternReviews, setPatternReviews] = useState<Review[]>([]);
  const [selectedThemeId, setSelectedThemeId] = useState<string | null>(null);
  const [patternReviewsLoading, setPatternReviewsLoading] = useState(false);
  const [filters, setFilters] = useState<ReviewFilters>(DEFAULT_FILTERS);
  const [view, setView] = useState<ViewMode>('patterns');
  const [loading, setLoading] = useState(true);
  const [themesLoading, setThemesLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);
  const [pipelineMessage, setPipelineMessage] = useState<string | null>(null);

  const sheetMeta = getSheetMeta();
  const selectedTheme = useMemo(
    () => themes.find((theme) => theme.id === selectedThemeId) ?? null,
    [themes, selectedThemeId],
  );

  const loadReviews = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (backendOnline) {
        const data = await fetchBackendReviews();
        setReviews(data);
      } else {
        const data = await fetchReviews();
        setReviews(data);
      }
      setLastSynced(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load reviews');
    } finally {
      setLoading(false);
    }
  }, [backendOnline]);

  const loadThemes = useCallback(async () => {
    if (!backendOnline) {
      setThemes([]);
      setThemesLoading(false);
      return;
    }

    setThemesLoading(true);
    try {
      const data = await fetchThemes();
      setThemes(data);
    } catch {
      setThemes([]);
    } finally {
      setThemesLoading(false);
    }
  }, [backendOnline]);

  const checkBackend = useCallback(async () => {
    try {
      await fetchHealth();
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }, []);

  const handleSelectPattern = useCallback(
    async (themeId: string | null) => {
      setSelectedThemeId(themeId);
      setPatternReviews([]);

      if (!themeId || !backendOnline) return;

      setPatternReviewsLoading(true);
      setError(null);

      try {
        const payload = await fetchThemeReviews(themeId);
        setPatternReviews(payload.reviews);
      } catch {
        setError('Unable to load reviews for this pattern');
        setPatternReviews([]);
      } finally {
        setPatternReviewsLoading(false);
      }
    },
    [backendOnline],
  );

  useEffect(() => {
    void checkBackend();
  }, [checkBackend]);

  useEffect(() => {
    void loadReviews();
  }, [loadReviews]);

  useEffect(() => {
    void loadThemes();
  }, [loadThemes]);

  const runRefresh = async () => {
    setRefreshing(true);
    setPipelineMessage(null);
    setError(null);

    try {
      if (backendOnline) {
        const result = await runPipelineRefresh();
        setPipelineMessage(
          `Pipeline complete: ${result.rows_ingested} new rows, ${result.new_clusters} patterns, ${result.themes_relabeled} labels updated.`,
        );
        await loadThemes();
        await loadReviews();
        if (selectedThemeId) {
          await handleSelectPattern(selectedThemeId);
        }
      } else {
        await loadReviews();
        setPipelineMessage('Backend offline — loaded latest sheet CSV only.');
      }
      setLastSynced(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Refresh failed');
    } finally {
      setRefreshing(false);
    }
  };

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
        loading={loading || refreshing}
        backendOnline={backendOnline}
        onRefresh={() => void runRefresh()}
      />

      <main className="app__main">
        <div className="view-tabs">
          <button
            type="button"
            className={`view-tabs__button ${view === 'patterns' ? 'view-tabs__button--active' : ''}`}
            onClick={() => setView('patterns')}
          >
            Patterns & Chat
          </button>
          <button
            type="button"
            className={`view-tabs__button ${view === 'discovery' ? 'view-tabs__button--active' : ''}`}
            onClick={() => {
              setView('discovery');
              setFilters(DEFAULT_FILTERS);
            }}
          >
            All reviews
          </button>
        </div>

        {pipelineMessage && <p className="pipeline-message">{pipelineMessage}</p>}
        {error && view === 'patterns' && selectedThemeId && (
          <p className="pipeline-message pipeline-message--error">{error}</p>
        )}

        {view === 'patterns' ? (
          <div className="app__insights">
            <PatternDashboard
              themes={themes}
              loading={themesLoading}
              selectedThemeId={selectedThemeId}
              selectedTheme={selectedTheme}
              patternReviews={patternReviews}
              reviewsLoading={patternReviewsLoading}
              onSelectTheme={(id) => void handleSelectPattern(id)}
            />
            <ChatPanel />
          </div>
        ) : (
          <>
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
          </>
        )}
      </main>
    </div>
  );
}
