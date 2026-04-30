import { useState } from 'react';

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

function CharacterPanel({ playerCharacter }) {
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

function CampaignPanel({ campaignState, selectedCampaign }) {
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

function MemoriesPanel({ memories }) {
  return (
    <section className="status-panel">
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

function ReadinessPanel({ shellReadiness }) {
  const readinessCards = [
    { label: "Generation Provider", value: shellReadiness.provider.label, detail: shellReadiness.provider.detail, tone: shellReadiness.provider.tone },
    { label: "world_bible.md", value: shellReadiness.worldBible.label, detail: shellReadiness.worldBible.detail, tone: shellReadiness.worldBible.tone },
    { label: "Canonical Campaign", value: shellReadiness.campaignSeed.label, detail: shellReadiness.campaignSeed.detail, tone: shellReadiness.campaignSeed.tone },
  ];
  return (
    <section className="status-panel">
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

function SystemPanel({ healthStatus, systemStatus }) {
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

const TABS = [
  { id: 'character', glyph: '◈', label: 'Field Readout' },
  { id: 'campaign', glyph: '◎', label: 'Current Brief' },
  { id: 'memories', glyph: '◉', label: 'Campaign Log' },
  { id: 'readiness', glyph: '⊙', label: 'GM Stack' },
  { id: 'system', glyph: '⊞', label: 'Machine State' },
];

export function StatusPanel({ campaignState, healthStatus, memories, selectedCampaign, shellReadiness, systemStatus }) {
  const [activeTab, setActiveTab] = useState(null);

  function handleTabClick(id) {
    setActiveTab((current) => (current === id ? null : id));
  }

  return (
    <aside className="status-stack">
      <nav className="sidebar-icon-rail">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`sidebar-icon-btn${activeTab === tab.id ? ' is-active' : ''}`}
            onClick={() => handleTabClick(tab.id)}
            title={tab.label}
            type="button"
          >
            {tab.glyph}
          </button>
        ))}
      </nav>
      {activeTab && (
        <div className="sidebar-popout">
          {activeTab === 'character' && (
            <CharacterPanel playerCharacter={campaignState?.player_character} />
          )}
          {activeTab === 'campaign' && (
            <CampaignPanel campaignState={campaignState} selectedCampaign={selectedCampaign} />
          )}
          {activeTab === 'memories' && (
            <MemoriesPanel memories={memories} />
          )}
          {activeTab === 'readiness' && (
            <ReadinessPanel shellReadiness={shellReadiness} />
          )}
          {activeTab === 'system' && (
            <SystemPanel healthStatus={healthStatus} systemStatus={systemStatus} />
          )}
        </div>
      )}
    </aside>
  );
}
