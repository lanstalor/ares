import { useEffect, useRef } from "react";
import { getCasteColorToken } from "../lib/uiTheme";

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

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

function buildNameColorMap(participants, speakerName, speakerCaste) {
  const map = new Map();

  function addVariant(name, color) {
    if (!name || typeof name !== "string") {
      return;
    }

    const trimmed = name.trim();
    if (trimmed.length < 3) {
      return;
    }

    if (!map.has(trimmed)) {
      map.set(trimmed, color);
    }
  }

  if (speakerName) {
    const color = getCasteColorToken(speakerCaste);
    const parts = speakerName.split(/\s+/).filter(Boolean);
    addVariant(speakerName, color);
    addVariant(parts[0], color);
  }

  for (const p of participants ?? []) {
    if (!p.name || p.tone === "system" || p.tone === "player") continue;
    const color = getCasteColorToken(p.caste);
    const parts = p.name.split(/\s+/).filter(Boolean);
    addVariant(p.name, color);
    addVariant(parts[0], color);
    addVariant(parts[parts.length - 1], color);
  }

  return map;
}

const CASTE_QUOTE_RE = /^\[(\w+)\]("[^"]*")$/;

function renderText(text, speaker, nameColorMap) {
  if (!text) return null;

  const names = nameColorMap ? [...nameColorMap.keys()].sort((a, b) => b.length - a.length) : [];
  const namePattern = names.length
    ? `(?<![\\w-])(?:${names.map(escapeRegExp).join("|")})(?![\\w-])`
    : null;

  // Match: [Caste]"quote", plain "quote", or known names, in priority order.
  const patternParts = [`\\[\\w+\\]"[^"]*"`, `"[^"]*"`];
  if (namePattern) patternParts.push(namePattern);
  const fullPattern = new RegExp(patternParts.join("|"), "g");

  const segments = [];
  let lastIndex = 0;
  let match;

  while ((match = fullPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }

    const value = match[0];
    if (value.startsWith("[")) {
      const parsed = CASTE_QUOTE_RE.exec(value);
      segments.push({ type: "caste-quote", caste: parsed?.[1] ?? "System", quote: parsed?.[2] ?? value });
    } else if (value.startsWith('"')) {
      segments.push({ type: "quote", value });
    } else {
      segments.push({ type: "name", value, color: nameColorMap?.get(value) });
    }

    lastIndex = match.index + value.length;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  if (segments.every((s) => s.type === "text")) return text;

  return segments.map((seg, i) => {
    if (seg.type === "caste-quote") {
      const color = getCasteColorToken(seg.caste);
      return (
        <span key={i} style={{ color, textShadow: `0 0 8px ${color}55` }}>
          {seg.quote}
        </span>
      );
    }
    if (seg.type === "quote") {
      return (
        <span key={i} className={`turn-dialogue turn-dialogue-${speaker}`}>
          {seg.value}
        </span>
      );
    }
    if (seg.type === "name") {
      return (
        <span key={i} style={{ color: seg.color, fontWeight: 500 }}>
          {seg.value}
        </span>
      );
    }
    return seg.value;
  });
}

export function TurnFeed({
  campaignName,
  isThinking,
  objective,
  participants,
  speakerCaste,
  speakerName,
  speakerRole,
  statusText,
  turns,
}) {
  const scrollRef = useRef(null);
  const prevTurnCountRef = useRef(0);

  useEffect(() => {
    const scrollEl = scrollRef.current;
    if (!scrollEl) return;

    const prevCount = prevTurnCountRef.current;
    const currCount = turns.length;

    if (currCount > prevCount) {
      const newSlice = turns.slice(prevCount);
      const firstNewGmOffset = newSlice.findIndex((t) => t.speaker === "gm");

      if (firstNewGmOffset >= 0) {
        const absIndex = prevCount + firstNewGmOffset;
        const el = scrollEl.querySelector(`[data-turn-index="${absIndex}"]`);
        if (el) {
          scrollEl.scrollTop = el.offsetTop - scrollEl.offsetTop;
          prevTurnCountRef.current = currCount;
          return;
        }
      }
    }

    scrollEl.scrollTop = scrollEl.scrollHeight;
    prevTurnCountRef.current = currCount;
  }, [turns, isThinking]);

  const nameColorMap = buildNameColorMap(participants, speakerName, speakerCaste);

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
            turns.map((turn, index) => {
              const avatar = getTurnAvatar(turn, speakerName, speakerCaste);

              return (
                <article
                  className={`turn turn-${turn.speaker}`}
                  data-turn-index={index}
                  key={turn.id}
                >
                  <div className="turn-avatar" style={{ borderColor: getCasteColorToken(avatar.caste) }}>
                    <span>{avatar.initials}</span>
                  </div>
                  <div className="turn-copy">
                    <div className="turn-meta">
                      <span style={{ color: getCasteColorToken(avatar.caste) }}>{avatar.name}</span>
                      <span>{formatTimestamp(turn.timestamp) ?? turn.meta ?? "Live"}</span>
                    </div>
                    <p>{renderText(turn.text, turn.speaker, nameColorMap)}</p>
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
