function formatTimestamp(value) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  return date.toLocaleString();
}

export function TurnFeed({ campaignName, statusText, turns }) {
  return (
    <section className="turn-feed">
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Turn Feed</p>
          <h2>{campaignName ?? "Live Narrative"}</h2>
        </div>
        <span className="panel-chip">{statusText}</span>
      </div>

      <div className="turn-list">
        {turns.length ? (
          turns.map((turn) => (
            <article className={`turn turn-${turn.speaker}`} key={turn.id}>
              <div className="turn-meta">
                <span>{turn.label}</span>
                <span>{formatTimestamp(turn.timestamp) ?? turn.meta ?? "Live"}</span>
              </div>
              {turn.location ? <p className="turn-location">{turn.location}</p> : null}
              <p>{turn.text}</p>
            </article>
          ))
        ) : (
          <article className="turn turn-system">
            <div className="turn-meta">
              <span>System</span>
              <span>Awaiting campaign</span>
            </div>
            <p>Create or select a campaign to open the live turn channel.</p>
          </article>
        )}
      </div>
    </section>
  );
}
