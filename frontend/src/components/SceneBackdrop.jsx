import { useState } from "react";

import { resolveSceneArt } from "../lib/sceneArtLibrary";
import { getCasteColorToken } from "../lib/uiTheme";

const TABS = [
  { id: "scene", label: "Scene" },
  { id: "character", label: "Character" },
  { id: "inventory", label: "Inventory" },
  { id: "stats", label: "Stats" },
  { id: "map", label: "Map" },
];

function SceneArt({ currentLocation, objective, sceneTone, selectedCampaign }) {
  const art = resolveSceneArt({ currentLocation, objective, sceneTone, selectedCampaign });

  return (
    <>
      <div className="scene-backdrop-art">
        <img
          alt={art.label}
          className="scene-backdrop-image"
          loading="eager"
          src={art.src}
        />
        <div className="scene-image-wash" />
        <div className="scene-grid" />
        <div className="scene-lights" />
        <div className="scene-sigil">ARES</div>
        <div className="scene-horizon" />
      </div>

      <div className="scene-backdrop-copy">
        <p className="eyebrow">Environment</p>
        <h2>{currentLocation ?? "Crescent Block / Callisto Depot District"}</h2>
        <p>
          {selectedCampaign?.tagline ??
            "Live scene art is selected from the current location and objective packet."}
        </p>
      </div>

      <dl className="scene-backdrop-meta">
        <div>
          <dt>Scene tone</dt>
          <dd>{sceneTone === "gold" ? "Imperial / official" : "Grounded / low-district"}</dd>
        </div>
        <div>
          <dt>Objective</dt>
          <dd>{objective ?? "Awaiting live mission objective"}</dd>
        </div>
      </dl>
    </>
  );
}

function CharacterView({ playerCharacter }) {
  if (!playerCharacter) {
    return <p className="scene-terminal-empty">No character packet loaded.</p>;
  }

  return (
    <div className="scene-data-panel">
      <div className="scene-character-card">
        <div className="scene-character-avatar" style={{ borderColor: getCasteColorToken(playerCharacter.race) }}>
          <span>{playerCharacter.name.slice(0, 2).toUpperCase()}</span>
        </div>
        <div>
          <p className="eyebrow">Operative File</p>
          <h2 style={{ color: getCasteColorToken(playerCharacter.race) }}>{playerCharacter.name}</h2>
          <p>{playerCharacter.race ?? "Unknown"} / {playerCharacter.character_class ?? "Unknown"}</p>
        </div>
      </div>
      <dl className="scene-data-grid">
        <div>
          <dt>Cover</dt>
          <dd>{playerCharacter.cover_identity ?? "Unregistered"}</dd>
        </div>
        <div>
          <dt>Notes</dt>
          <dd>{playerCharacter.notes ?? "No notes in local packet"}</dd>
        </div>
      </dl>
    </div>
  );
}

function InventoryView({ playerCharacter }) {
  const items = (playerCharacter?.inventory_summary ?? "No inventory packet loaded")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return (
    <div className="scene-data-panel">
      <p className="eyebrow">Inventory</p>
      <div className="inventory-grid">
        {items.map((item) => (
          <div className="inventory-slot" key={item}>
            <span>▣</span>
            <strong>{item}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatsView({ playerCharacter, objective }) {
  const hp = playerCharacter ? `${playerCharacter.current_hp ?? "?"}/${playerCharacter.max_hp ?? "?"}` : "Unknown";
  const cover = playerCharacter?.cover_integrity ?? "Unknown";

  return (
    <div className="scene-data-panel">
      <p className="eyebrow">Cell Telemetry</p>
      <dl className="scene-data-grid">
        <div>
          <dt>HP</dt>
          <dd>{hp}</dd>
        </div>
        <div>
          <dt>Cover integrity</dt>
          <dd>{cover}</dd>
        </div>
        <div>
          <dt>Objective</dt>
          <dd>{objective ?? "No objective loaded"}</dd>
        </div>
      </dl>
    </div>
  );
}

function MapView({ currentLocation }) {
  return (
    <div className="scene-map-view">
      <div className="map-grid" />
      <div className="map-node map-node-active">Crescent Block</div>
      <div className="map-node map-node-dim">Ceres Row</div>
      <div className="map-node map-node-cold">Tram Spine</div>
      <p className="scene-map-label">{currentLocation ?? "Unknown sector"}</p>
    </div>
  );
}

export function SceneBackdrop({ campaignState, currentLocation, objective, sceneTone, selectedCampaign }) {
  const [activeTab, setActiveTab] = useState("scene");
  const playerCharacter = campaignState?.player_character;

  return (
    <section className={`scene-backdrop-panel frame-screen tone-${sceneTone}`}>
      <div className="scene-tabs" role="tablist" aria-label="Scene display mode">
        {TABS.map((tab) => (
          <button
            aria-selected={activeTab === tab.id}
            className={`scene-tab ${activeTab === tab.id ? "is-active" : ""}`}
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            role="tab"
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "scene" ? (
        <SceneArt
          currentLocation={currentLocation}
          objective={objective}
          sceneTone={sceneTone}
          selectedCampaign={selectedCampaign}
        />
      ) : null}
      {activeTab === "character" ? <CharacterView playerCharacter={playerCharacter} /> : null}
      {activeTab === "inventory" ? <InventoryView playerCharacter={playerCharacter} /> : null}
      {activeTab === "stats" ? <StatsView objective={objective} playerCharacter={playerCharacter} /> : null}
      {activeTab === "map" ? <MapView currentLocation={currentLocation} /> : null}
    </section>
  );
}
