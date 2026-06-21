interface HeaderProps {
  sheetName: string;
  sourceLabel: string;
  lastSynced: Date | null;
  loading: boolean;
  onRefresh: () => void;
}

export function Header({
  sheetName,
  sourceLabel,
  lastSynced,
  loading,
  onRefresh,
}: HeaderProps) {
  return (
    <header className="header">
      <div className="header__brand">
        <div className="header__logo" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <div>
          <p className="header__eyebrow">NL · AI Review Engine</p>
          <h1>Review Discovery Engine</h1>
          <p className="header__subtitle">
            Live feed from <strong>{sheetName}</strong> · {sourceLabel}
          </p>
        </div>
      </div>

      <div className="header__actions">
        {lastSynced && (
          <p className="header__sync">
            Synced {lastSynced.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
        <button
          type="button"
          className="button button--primary"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing…' : 'Refresh data'}
        </button>
      </div>
    </header>
  );
}
