import { useEffect, useRef } from "react";
import { getCasteColorToken } from "../lib/uiTheme";

function formatTimestamp(value) {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  return date.toLocaleString();
}

function getTurnAvatar(turn, speakerName, speakerCaste) {
  if (turn.speaker === "player") {
    return {
      initials: (speakerName ?? "DA").slice(0, 2).toUpperCase(),
      name: speakerName ?? "Player",
      caste: speakerCaste ?? "HighRed",
    };
  }

  if (turn.speaker === "gm") {
    return {
      initials: "GM",
      name: "Ares Relay",
      caste: "System",
    };
  }

  if (turn.speaker === "system-location") {
    return {
      initials: "LO",
      name: "Location",
      caste: "Blue",
    };
  }

  if (turn.speaker === "system-clock") {
    return {
      initials: "CL",
      name: "Clock",
      caste: "Gold",
    };
  }

  return {
    initials: "AR",
    name: turn.label ?? "System",
    caste: "System",
  };
}

function renderText(text, speaker) {
  if (!text) return null;

  const segments = [];
  const quoteRe = /"[^"]*"/g;
  let lastIndex = 0;
  let match;

  while ((match = quoteRe.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }
    segments.push({ type: "quote", value: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  if (segments.every((s) => s.type === "text")) {
    return text;
  }

  return segments.map((seg, i) =>
    seg.type === "quote" ? (
      <span key={i} className={`turn-dialogue turn-dialogue-${speaker}`}>{seg.value}</span>
    ) : (
      seg.value
    ),
  );
}

export function TurnFeed({
  campaignName,
  isThinking,
  objective,
  speakerCaste,
  speakerName,
  speakerRole,
  statusText,
  turns,
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [turns, isThinking]);

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

      <div className="turn-feed-scroll" ref={scrollRef}>
        <div className="turn-list">
          {turns.length === 0 ? (
            <article className="turn turn-gm turn-opening">
              <div className="turn-avatar" style={{ borderColor: getCasteColorToken("System") }}>
                <span>GM</span>
              </div>
              <div className="turn-copy">
                <div className="turn-meta">
                  <span style={{ color: getCasteColorToken("System") }}>Ares Relay</span>
                  <span>Channel open</span>
                </div>
                {objective ? (
                  <p className="turn-objective-prompt">
                    <span className="turn-objective-label">Objective — </span>{objective}
                  </p>
                ) : null}
                <p>The relay is armed and the hidden-state engine is live. Describe your first move.</p>
              </div>
            </article>
          ) : (
            turns.map((turn) => {
              const avatar = getTurnAvatar(turn, speakerName, speakerCaste);

              return (
                <article className={`turn turn-${turn.speaker}`} key={turn.id}>
                  <div className="turn-avatar" style={{ borderColor: getCasteColorToken(avatar.caste) }}>
                    <span>{avatar.initials}</span>
                  </div>
                  <div className="turn-copy">
                    <div className="turn-meta">
                      <span style={{ color: getCasteColorToken(avatar.caste) }}>{avatar.name}</span>
                      <span>{formatTimestamp(turn.timestamp) ?? turn.meta ?? "Live"}</span>
                    </div>
                    {turn.location ? <p className="turn-location">{turn.location}</p> : null}
                    <p>{renderText(turn.text, turn.speaker)}</p>
                  </div>
                </article>
              );
            })
          )}

          {isThinking ? (
            <article className="turn turn-gm turn-thinking">
              <div className="turn-avatar" style={{ borderColor: getCasteColorToken("System") }}>
                <span>GM</span>
              </div>
              <div className="turn-copy">
                <div className="turn-meta">
                  <span style={{ color: getCasteColorToken("System") }}>Ares Relay</span>
                  <span>Processing</span>
                </div>
                <p className="thinking-dots" aria-label="GM is thinking">
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                </p>
              </div>
            </article>
          ) : null}
        </div>
      </div>
    </section>
  );
}
