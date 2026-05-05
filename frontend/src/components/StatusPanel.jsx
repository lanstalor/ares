import { useState } from "react";
import { AssetOverlay } from "./AssetOverlay";

function renderFlag(value) {
  return value ? "enabled" : "disabled";
}

function renderMetricBar(current, max, segments = 10) {
  if (typeof current !== "number" || typeof max !== "number" || max <= 0) {
    return "unknown";
  }
  const safeCurrent = Math.max(0, Math.min(current, max));
  const filledCount = Math.round((safeCurrent / max) * segments);
  const filled = "■".repeat(filledCount);
  const empty = "□".repeat(Math.max(segments - filledCount, 0));
  return `${filled}${empty} ${safeCurrent}/${max}`;
}

function renderIntegrityBar(value, segments = 10) {
  if (typeof value !== "number") return "unknown";
  const normalized = Math.max(0, Math.min(value, 10));
  const filledCount = Math.round((normalized / 10) * segments);
  const filled = "■".repeat(filledCount);
  const empty = "□".repeat(Math.max(segments - filledCount, 0));
  return `${filled}${empty} ${normalized}/10`;
}

function CharacterPanel({ assetOverlayMode, playerCharacter }) {
  const sections = [
    ["Name", playerCharacter?.name ?? "No operative loaded"],
    ["Race", playerCharacter?.race ?? "Unknown"],
    ["Class", playerCharacter?.character_class ?? "Unknown"],
    ["Cover Identity", playerCharacter?.cover_identity ?? "No cover established"],
    ["HP", renderMetricBar(playerCharacter?.current_hp, playerCharacter?.max_hp)],
    ["Cover Integrity", renderIntegrityBar(playerCharacter?.cover_integrity)],
  ];
  return (
    <section className="status-panel">
      {assetOverlayMode ? <AssetOverlay frameId="statusPanel" /> : null}
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Operative Status</p>
          <h2>Field Readout</h2>
        </div>
        {playerCharacter ? <span className="panel-chip">live</span> : null}
      </div>
      <dl className="status-grid">
        {sections.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd className={label === "HP" || label === "Cover Integrity" ? "status-meter" : undefined}>
              {value}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function CampaignPanel({ assetOverlayMode, campaignState, selectedCampaign }) {
  const activeCampaign = campaignState?.campaign ?? selectedCampaign;
  const sections = [
    ["Campaign", activeCampaign?.name ?? "No active campaign"],
    ["Tagline", activeCampaign?.tagline ?? "None loaded"],
    ["Current Date", activeCampaign ? `${activeCampaign.current_date_pce} PCE` : "N/A"],
    ["Current Location", campaignState?.current_location ?? activeCampaign?.current_location_label ?? "Unknown"],
    ["Active Objective", campaignState?.active_objective ?? "No objective published"],
    ["Hidden Summary", campaignState?.hidden_state_summary ? "Sealed by backend" : "No sealed summary loaded"],
  ];
  return (
    <section className="status-panel">
      {assetOverlayMode ? <AssetOverlay frameId="statusPanel" /> : null}
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Campaign State</p>
          <h2>Current Brief</h2>
        </div>
        {activeCampaign ? <span className="panel-chip">selected</span> : null}
      </div>
      <dl className="status-grid">
        {sections.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function MemoriesPanel({ assetOverlayMode, memories }) {
  return (
    <section className="status-panel">
      {assetOverlayMode ? <AssetOverlay frameId="statusPanel" /> : null}
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Campaign Log</p>
          <h2>Memories</h2>
        </div>
        {memories && memories.length > 0 ? <span className="panel-chip">{memories.length}</span> : null}
      </div>
      {memories && memories.length > 0 ? (
        <ul className="status-memory-list">
          {memories.map((memory) => (
            <li key={memory.id} className="status-memory-item">{memory.content}</li>
          ))}
        </ul>
      ) : (
        <p className="hint">No memories recorded yet.</p>
      )}
    </section>
  );
}

function ReadinessPanel({ assetOverlayMode, shellReadiness }) {
  const readinessCards = [
    { label: "Generation Provider", value: shellReadiness.provider.label, detail: shellReadiness.provider.detail, tone: shellReadiness.provider.tone },
    { label: "world_bible.md", value: shellReadiness.worldBible.label, detail: shellReadiness.worldBible.detail, tone: shellReadiness.worldBible.tone },
    { label: "Canonical Campaign", value: shellReadiness.campaignSeed.label, detail: shellReadiness.campaignSeed.detail, tone: shellReadiness.campaignSeed.tone },
  ];
  return (
    <section className="status-panel">
      {assetOverlayMode ? <AssetOverlay frameId="statusPanel" /> : null}
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Readiness</p>
          <h2>GM Stack</h2>
        </div>
      </div>
      <div className="readiness-grid">
        {readinessCards.map((card) => (
          <article className="readiness-card" key={card.label}>
            <p className="panel-label">{card.label}</p>
            <p className={`readiness-value is-${card.tone}`}>{card.value}</p>
            <p className="hint">{card.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function SystemPanel({ assetOverlayMode, healthStatus, systemStatus }) {
  const sections = [
    ["Health", healthStatus?.status ?? "offline"],
    ["Application", systemStatus?.app_name ?? "unknown"],
    ["Environment", systemStatus?.environment ?? "unknown"],
    ["Embeddings", systemStatus?.embedding_provider ?? "unknown"],
    ["World Bible Path", systemStatus?.world_bible_path ?? "unavailable"],
    ["Hidden State", renderFlag(systemStatus?.hidden_state_enabled)],
    ["Multi-Agent", renderFlag(systemStatus?.multi_agent_enabled)],
  ];
  return (
    <section className="status-panel">
      {assetOverlayMode ? <AssetOverlay frameId="statusPanel" /> : null}
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">System Status</p>
          <h2>Machine State</h2>
        </div>
        <span className={`panel-chip ${healthStatus?.status === "ok" ? "is-good" : "is-bad"}`}>
          {healthStatus?.status === "ok" ? "Connected" : "Offline"}
        </span>
      </div>
      <dl className="status-grid">
        {sections.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

export function StatusPanel({
  assetOverlayMode,
  campaignState,
  healthStatus,
  memories,
  selectedCampaign,
  shellReadiness,
  systemStatus,
}) {
  const [activeTab, setActiveTab] = useState("character");
  const [isOpen, setIsOpen] = useState(false);

  const tabs = [
    { id: "character", label: "OP", title: "Operative Status" },
    { id: "campaign", label: "BR", title: "Campaign Brief" },
    { id: "memories", label: "LG", title: "Campaign Log" },
    { id: "readiness", label: "RD", title: "GM Stack" },
    { id: "system", label: "SY", title: "System State" },
  ];

  const activeTabConfig = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  function handleTabToggle(nextTab) {
    if (nextTab === activeTab) {
      setIsOpen((current) => !current);
      return;
    }

    setActiveTab(nextTab);
    setIsOpen(true);
  }

  function renderPanel() {
    switch (activeTab) {
      case "character": return <CharacterPanel assetOverlayMode={assetOverlayMode} playerCharacter={campaignState?.player_character} />;
      case "campaign": return <CampaignPanel assetOverlayMode={assetOverlayMode} campaignState={campaignState} selectedCampaign={selectedCampaign} />;
      case "memories": return <MemoriesPanel assetOverlayMode={assetOverlayMode} memories={memories} />;
      case "readiness": return <ReadinessPanel assetOverlayMode={assetOverlayMode} shellReadiness={shellReadiness} />;
      case "system": return <SystemPanel assetOverlayMode={assetOverlayMode} healthStatus={healthStatus} systemStatus={systemStatus} />;
      default: return null;
    }
  }

  return (
    <aside className="status-stack utility-column" aria-label="Utility telemetry">
      <nav className="sidebar-icon-rail frame-module" aria-label="Panel tabs">
        {assetOverlayMode ? <AssetOverlay frameId="utilityRail" /> : null}
        {tabs.map((tab) => (
          <button
            key={tab.id}
            aria-controls="utility-panel-popout"
            aria-expanded={isOpen && activeTab === tab.id}
            className={`sidebar-icon-btn frame-chip${isOpen && activeTab === tab.id ? " is-active" : ""}`}
            onClick={() => handleTabToggle(tab.id)}
            title={tab.title}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </nav>
      {isOpen ? (
        <div className="sidebar-popout frame-module is-open" id="utility-panel-popout">
          {assetOverlayMode ? <AssetOverlay frameId="utilityPopout" /> : null}
          <div className="sidebar-popout-header">
            <span className="sidebar-popout-title">{activeTabConfig.title}</span>
            <button
              aria-label="Close utility panel"
              className="sidebar-popout-close"
              onClick={() => setIsOpen(false)}
              type="button"
            >
              ×
            </button>
          </div>
          {renderPanel()}
        </div>
      ) : null}
    </aside>
  );
}
