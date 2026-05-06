import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { AssetOverlay } from "./AssetOverlay";
import { DISPOSITION_META, DISPOSITION_ORDER, getCasteColorToken } from "../lib/uiTheme";
import { regeneratePortrait } from "../lib/api";

function PortraitImage({ portraitSrc, characterId, campaignId, name }) {
  const [imageSrc, setImageSrc] = useState(portraitSrc);
  const [isLoading, setIsLoading] = useState(!!portraitSrc);
  const [failedToLoad, setFailedToLoad] = useState(false);

  useEffect(() => {
    if (!portraitSrc) {
      setIsLoading(false);
      return;
    }

    // Try to load the image
    const img = new Image();
    img.onload = () => {
      setImageSrc(portraitSrc);
      setIsLoading(false);
    };
    img.onerror = async () => {
      // If 404 and we have characterId/campaignId, try to regenerate
      if (characterId && campaignId && !failedToLoad) {
        try {
          await regeneratePortrait(campaignId, characterId);
          setFailedToLoad(false);
          // Retry loading after a short delay
          setTimeout(() => {
            const retryImg = new Image();
            retryImg.onload = () => {
              setImageSrc(portraitSrc);
              setIsLoading(false);
            };
            retryImg.onerror = () => {
              setIsLoading(false);
              setFailedToLoad(true);
            };
            retryImg.src = portraitSrc;
          }, 500);
        } catch {
          setIsLoading(false);
          setFailedToLoad(true);
        }
      } else {
        setIsLoading(false);
        setFailedToLoad(true);
      }
    };
    img.src = portraitSrc;
  }, [portraitSrc, characterId, campaignId, failedToLoad]);

  if (!imageSrc) {
    return null;
  }

  return <img alt="" className="participant-portrait-image" src={imageSrc} />;
}

function hpPercent(hp) {
  if (!hp || !hp.max) return 0;
  return Math.max(0, Math.min(100, Math.round((hp.current / hp.max) * 100)));
}

function hpTone(hp) {
  const pct = hpPercent(hp);
  if (pct >= 66) return "good";
  if (pct >= 33) return "warn";
  return "bad";
}

function HpMeter({ hp, compact = false }) {
  if (!hp) return null;
  const pct = hpPercent(hp);
  const tone = hpTone(hp);
  return (
    <div className={`participant-hp tone-${tone} ${compact ? "is-compact" : ""}`}>
      <div className="participant-hp-bar" aria-hidden="true">
        <div className="participant-hp-fill" style={{ width: `${pct}%` }} />
      </div>
      {compact ? null : (
        <span className="participant-hp-readout">
          {hp.current}/{hp.max} HP
        </span>
      )}
    </div>
  );
}

function DispositionMeter({ disposition, compact = false }) {
  if (!disposition) return null;
  const meta = DISPOSITION_META[disposition];
  if (!meta) return null;
  if (compact) {
    return (
      <span className={`participant-disposition-chip tone-${meta.tone}`}>
        <span className="participant-disposition-dot" aria-hidden="true" />
        {meta.label}
      </span>
    );
  }
  return (
    <div className={`participant-disposition-meter tone-${meta.tone}`}>
      <div className="participant-disposition-track" aria-hidden="true">
        {DISPOSITION_ORDER.map((step, index) => (
          <span
            key={step}
            className={`participant-disposition-step ${index === meta.index ? "is-current" : ""} ${
              index < meta.index ? "is-trailing" : ""
            }`}
          />
        ))}
      </div>
    </div>
  );
}

function ParticipantModal({ participant, onClose }) {
  useEffect(() => {
    function handleKeydown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  }, [onClose]);

  if (!participant) {
    return null;
  }

  return (
    <div className="participant-modal-backdrop" onClick={onClose} role="presentation">
      <section className="participant-modal" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
        <button aria-label="Close about panel" className="participant-modal-close" onClick={onClose} type="button">
          ×
        </button>

        <div className="participant-modal-header">
          <div className={`participant-portrait tone-${participant.tone} participant-modal-avatar`}>
            {participant.portraitSrc ? (
              <PortraitImage
                portraitSrc={participant.portraitSrc}
                characterId={participant.id}
                campaignId={participant.campaignId}
                name={participant.name}
              />
            ) : null}
            {(!participant.portraitSrc || !participant.portraitSrc.startsWith("/portraits/")) && (
              <span>{participant.name.slice(0, 2).toUpperCase()}</span>
            )}
            {participant.level ? (
              <span className="participant-level-badge participant-level-badge-lg">
                {participant.level}
              </span>
            ) : null}
          </div>
          <div>
            <p className="eyebrow">About</p>
            <h2 style={{ color: getCasteColorToken(participant.caste) }}>{participant.name}</h2>
            <p className="participant-modal-subtitle">
              {participant.caste} / {participant.role}
              {participant.level ? <span className="participant-modal-level"> · Lvl {participant.level}</span> : null}
            </p>
          </div>
        </div>

        <div className="participant-modal-body">
          {participant.hp || participant.disposition ? (
            <div className="participant-modal-stats">
              {participant.hp ? (
                <div className="participant-modal-stat">
                  <div className="participant-modal-stat-row">
                    <span className="participant-modal-stat-label">Health</span>
                    <span className="participant-modal-stat-value">
                      {participant.hp.current}/{participant.hp.max}
                    </span>
                  </div>
                  <HpMeter hp={participant.hp} compact />
                </div>
              ) : null}
              {participant.disposition ? (
                <div className="participant-modal-stat">
                  <div className="participant-modal-stat-row">
                    <span className="participant-modal-stat-label">Disposition</span>
                    <span className="participant-modal-stat-value">
                      {DISPOSITION_META[participant.disposition]?.label}
                    </span>
                  </div>
                  <DispositionMeter disposition={participant.disposition} />
                </div>
              ) : null}
            </div>
          ) : null}

          <dl className="participant-modal-grid">
            <div>
              <dt>Status</dt>
              <dd>{participant.active ? "Active speaker" : "In scene"}</dd>
            </div>
            <div>
              <dt>Faction</dt>
              <dd>{participant.caste}</dd>
            </div>
            <div className="participant-modal-grid-wide">
              <dt>Notes</dt>
              <dd>
                {participant.id === "relay"
                  ? "This is the encrypted runtime link. It is the channel boundary between the visible player surface and the hidden GM state."
                  : `Operational profile for ${participant.name}.`}
              </dd>
            </div>
          </dl>
        </div>
      </section>
    </div>
  );
}

function ParticipantCard({ participant, onOpen }) {
  const showStats = participant.hp || participant.disposition;
  return (
    <article className={`participant-card ${participant.active ? "is-active" : ""}`}>
      <button
        className={`participant-portrait tone-${participant.tone} participant-avatar-button`}
        onClick={() => onOpen(participant)}
        type="button"
      >
        {participant.portraitSrc ? (
          <PortraitImage
            portraitSrc={participant.portraitSrc}
            characterId={participant.id}
            campaignId={participant.campaignId}
            name={participant.name}
          />
        ) : null}
        {(!participant.portraitSrc || !participant.portraitSrc.startsWith("/portraits/")) && (
          <span>{participant.name.slice(0, 2).toUpperCase()}</span>
        )}
        {participant.level ? (
          <span className="participant-level-badge" aria-label={`Level ${participant.level}`}>
            {participant.level}
          </span>
        ) : null}
      </button>

      <div className="participant-copy">
        <p className="participant-name" style={{ color: getCasteColorToken(participant.caste) }}>
          {participant.name}
        </p>
        <p className="participant-role">{participant.role}</p>
        {showStats ? (
          <div className="participant-stats">
            <HpMeter hp={participant.hp} compact />
            <DispositionMeter disposition={participant.disposition} compact />
          </div>
        ) : (
          <p className={`participant-status ${participant.active ? "is-active" : ""}`}>
            {participant.active ? "Active speaker" : "In scene"}
          </p>
        )}
      </div>
    </article>
  );
}

export function ParticipantStrip({ assetOverlayMode, participants, sceneTone }) {
  const [selectedParticipant, setSelectedParticipant] = useState(null);

  return (
    <section className={`participant-strip tone-${sceneTone}`}>
      {assetOverlayMode ? <AssetOverlay frameId="presenceBar" /> : null}
      <div className="participant-strip-layout">
        <div className="participant-strip-header">
          <div className="panel-chrome">
            <h2>Scene Presence</h2>
          </div>
        </div>

        <div className="participant-scroll">
          {participants.map((participant) => (
            <ParticipantCard key={participant.id} participant={participant} onOpen={setSelectedParticipant} />
          ))}
        </div>
      </div>

      {selectedParticipant
        ? createPortal(
            <ParticipantModal participant={selectedParticipant} onClose={() => setSelectedParticipant(null)} />,
            document.body,
          )
        : null}
    </section>
  );
}
