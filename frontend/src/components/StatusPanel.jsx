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
  if (typeof value !== "number") {
    return "unknown";
  }

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
          <p className="eyebrow">Character Status</p>
          <h2>Operative Readout</h2>
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

export function StatusPanel({ campaignState, healthStatus, selectedCampaign, systemStatus }) {
  const backendSections = [
    ["Health", healthStatus?.status ?? "offline"],
    ["Environment", systemStatus?.environment ?? "unknown"],
    ["GM Provider", systemStatus?.ai_generation_provider ?? "unknown"],
    ["Embeddings", systemStatus?.embedding_provider ?? "unknown"],
    ["Hidden State", renderFlag(systemStatus?.hidden_state_enabled)],
    ["Multi-Agent", renderFlag(systemStatus?.multi_agent_enabled)],
  ];

  const campaignSections = [
    ["Campaign", selectedCampaign?.name ?? "No active campaign"],
    ["Tagline", selectedCampaign?.tagline ?? "None loaded"],
    ["Current Date", selectedCampaign ? `${selectedCampaign.current_date_pce} PCE` : "N/A"],
    ["Current Location", campaignState?.current_location ?? "Unknown"],
    ["Active Objective", campaignState?.active_objective ?? "No objective published"],
    [
      "Hidden Summary",
      campaignState?.hidden_state_summary ? "Sealed by backend" : "No sealed summary loaded",
    ],
  ];

  return (
    <aside className="status-stack">
      <section className="status-panel">
        <div className="panel-chrome">
          <div>
            <p className="eyebrow">System Status</p>
            <h2>Backend Link</h2>
          </div>
          <span className={`panel-chip ${healthStatus?.status === "ok" ? "is-good" : "is-bad"}`}>
            {healthStatus?.status === "ok" ? "Connected" : "Offline"}
          </span>
        </div>
        <dl className="status-grid">
          {backendSections.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <CharacterPanel playerCharacter={campaignState?.player_character} />

      <section className="status-panel">
        <div className="panel-chrome">
          <div>
            <p className="eyebrow">Campaign State</p>
            <h2>Active Cell</h2>
          </div>
          {selectedCampaign ? <span className="panel-chip">selected</span> : null}
        </div>
        <dl className="status-grid">
          {campaignSections.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </aside>
  );
}
