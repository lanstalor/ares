import { getCasteColorToken } from "../lib/uiTheme";

function formatTimestamp(value) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  return date.toLocaleString();
}

export function TurnFeed({ campaignName, speakerCaste, speakerName, speakerRole, statusText, turns }) {
  return (
    <section className="turn-feed">
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Narrative Feed</p>
          <h2>{campaignName ?? "Live GM Channel"}</h2>
        </div>
        <span className="panel-chip">{statusText}</span>
      </div>

      <article className="speaker-card">
        <div className="speaker-portrait">
          <span>{(speakerName ?? "AR").slice(0, 2).toUpperCase()}</span>
        </div>
        <div className="speaker-copy">
          <p className="speaker-kicker">Current moment</p>
          <p className="speaker-name" style={{ color: getCasteColorToken(speakerCaste) }}>
            {speakerName ?? "Ares Runtime"}
          </p>
          <p className="speaker-meta">
            {speakerCaste ?? "System"} / {speakerRole ?? "Live story conduit"}
          </p>
        </div>
        <div className="speaker-waveform" aria-hidden="true" />
      </article>

      <div className="turn-feed-scroll">
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
              <p>Load the canonical campaign or select a cell to open the live narrative channel.</p>
            </article>
          )}
        </div>
      </div>
    </section>
  );
}
