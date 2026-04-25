import { getCasteColorToken } from "../lib/uiTheme";

function ParticipantCard({ participant }) {
  return (
    <article className={`participant-card ${participant.active ? "is-active" : ""}`}>
      <div className={`participant-portrait tone-${participant.tone}`}>
        <span>{participant.name.slice(0, 2).toUpperCase()}</span>
      </div>
      <div className="participant-copy">
        <p className="participant-name" style={{ color: getCasteColorToken(participant.caste) }}>
          {participant.name}
        </p>
        <span className={`participant-status ${participant.active ? "is-active" : ""}`}>
          {participant.active ? "Active speaker" : "In scene"}
        </span>
        <p className="participant-meta">
          <span>{participant.caste}</span>
          <span>{participant.role}</span>
        </p>
      </div>
    </article>
  );
}

export function ParticipantStrip({ participants, sceneTone }) {
  return (
    <section className={`participant-strip tone-${sceneTone}`}>
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Participants</p>
          <h2>Scene Presence</h2>
        </div>
        <span className="panel-chip">{participants.length} visible</span>
      </div>

      <div className="participant-scroll">
        {participants.map((participant) => (
          <ParticipantCard key={participant.id} participant={participant} />
        ))}
      </div>
    </section>
  );
}
