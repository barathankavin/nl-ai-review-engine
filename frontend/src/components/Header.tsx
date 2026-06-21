interface HeaderProps {
  sheetName: string;
  sourceLabel: string;
  lastSynced: Date | null;
  loading: boolean;
  backendOnline?: boolean;
  onRefresh: () => void;
}

export function Header({
  sheetName,
  sourceLabel,
  lastSynced,
  loading,
  backendOnline = false,
  onRefresh,
}: HeaderProps) {
  return (
    <header className="header">
      <div className="header__brand">
        <img
          src="/spotify-icon.png"
          alt="Spotify"
          className="header__logo"
          width={48}
          height={48}
        />
        <div className="header__brand-text">
          <h1 className="header__title">
            <span className="header__title-main">AI-Powered Review Discovery Engine</span>
            <span className="header__title-accent"> - Spotify</span>
          </h1>
          <p className="header__subtitle">
            {sheetName} · {sourceLabel}
          </p>
        </div>
      </div>

      <div className="header__actions">
        <span className={`pill ${backendOnline ? 'pill--online' : 'pill--offline'}`}>
          {backendOnline ? 'Live pipeline' : 'Offline'}
        </span>
        {lastSynced && (
          <p className="header__sync">
            Updated {lastSynced.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
        <button
          type="button"
          className="btn btn--primary"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Syncing…' : 'Sync data'}
        </button>
      </div>
    </header>
  );
}
