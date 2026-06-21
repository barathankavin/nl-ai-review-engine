import type { ReviewFilters, SortOption } from '../types/review';

interface FilterPanelProps {
  filters: ReviewFilters;
  onChange: (filters: ReviewFilters) => void;
}

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'rating-high', label: 'Highest rating' },
  { value: 'rating-low', label: 'Lowest rating' },
  { value: 'helpful', label: 'Most helpful' },
];

export function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const update = (patch: Partial<ReviewFilters>) => onChange({ ...filters, ...patch });

  return (
    <aside className="filter-panel">
      <div className="filter-panel__section">
        <label className="field">
          <span>Search reviews</span>
          <input
            type="search"
            placeholder="Keywords, usernames, replies…"
            value={filters.query}
            onChange={(event) => update({ query: event.target.value })}
          />
        </label>
      </div>

      <div className="filter-panel__section">
        <p className="filter-panel__heading">Rating</p>
        <div className="chip-group">
          {[null, 1, 2, 3, 4, 5].map((score) => {
            const active = filters.minScore === score && filters.maxScore === score;
            const label = score === null ? 'All' : `${score}★`;

            return (
              <button
                key={label}
                type="button"
                className={`chip ${active ? 'chip--active' : ''}`}
                onClick={() =>
                  update({
                    minScore: score,
                    maxScore: score,
                  })
                }
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="filter-panel__section">
        <p className="filter-panel__heading">Developer reply</p>
        <div className="chip-group">
          {(['all', 'yes', 'no'] as const).map((value) => (
            <button
              key={value}
              type="button"
              className={`chip ${filters.hasReply === value ? 'chip--active' : ''}`}
              onClick={() => update({ hasReply: value })}
            >
              {value === 'all' ? 'All' : value === 'yes' ? 'With reply' : 'No reply'}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-panel__section">
        <label className="field">
          <span>Sort by</span>
          <select
            value={filters.sort}
            onChange={(event) => update({ sort: event.target.value as SortOption })}
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        className="button button--ghost"
        onClick={() =>
          onChange({
            query: '',
            minScore: null,
            maxScore: null,
            hasReply: 'all',
            sort: 'newest',
          })
        }
      >
        Reset filters
      </button>
    </aside>
  );
}
