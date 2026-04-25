function formatSeedResult(lastSeedResult) {
  if (!lastSeedResult) {
    return "No seed run recorded in this browser session.";
  }

  return `${lastSeedResult.campaign_name} imported from ${lastSeedResult.source_path}`;
}

export function CampaignConsole({
  campaigns,
  createForm,
  creatingCampaign,
  lastSeedResult,
  loadingCampaigns,
  loadingShell,
  loadingState,
  onCreateCampaign,
  onFormChange,
  onRefreshActiveCampaign,
  onRefreshShell,
  onSeedWorldBible,
  onSelectCampaign,
  seedingWorldBible,
  selectedCampaignId,
  shellReadiness,
  worldBibleReady,
}) {
  return (
    <section className="status-panel">
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">GM Control</p>
          <h2>Campaign Lattice</h2>
        </div>
        <span className="panel-chip">{loadingCampaigns ? "Syncing" : `${campaigns.length} cells loaded`}</span>
      </div>

      <div className="campaign-console">
        <div className="campaign-list">
          {campaigns.length ? (
            campaigns.map((campaign) => (
              <button
                className={`campaign-row ${campaign.id === selectedCampaignId ? "is-active" : ""}`}
                key={campaign.id}
                onClick={() => onSelectCampaign(campaign.id)}
                type="button"
              >
                <span className="campaign-row-name">{campaign.name}</span>
                <span className="campaign-row-meta">
                  {campaign.current_date_pce} PCE
                  {campaign.hidden_state_enabled ? " / hidden" : ""}
                </span>
              </button>
            ))
          ) : (
            <p className="empty-state">
              No campaign is loaded yet. Seed the canonical world bible or stage a fallback cell.
            </p>
          )}
        </div>

        <form className="campaign-form" onSubmit={onCreateCampaign}>
          <label className="panel-label" htmlFor="campaign-name">
            Draft fallback campaign
          </label>
          <input
            id="campaign-name"
            maxLength={200}
            name="name"
            onChange={onFormChange}
            placeholder="The Melt / Cell Gamma"
            value={createForm.name}
          />
          <input
            maxLength={255}
            name="tagline"
            onChange={onFormChange}
            placeholder="Short operator note or moodline"
            value={createForm.tagline}
          />
          <button disabled={creatingCampaign || !createForm.name.trim()} type="submit">
            {creatingCampaign ? "Creating..." : "Create fallback"}
          </button>
        </form>

        <div className="campaign-seed-tools">
          <p className="panel-label">Canonical Loadout</p>
          <p className="hint">
            {worldBibleReady
              ? "Import the authored campaign frame directly from world_bible.md."
              : "Backend cannot see world_bible.md yet."}
          </p>
          <button
            disabled={seedingWorldBible || !worldBibleReady}
            onClick={onSeedWorldBible}
            type="button"
          >
            {seedingWorldBible ? "Seeding..." : "Load canonical campaign"}
          </button>
          <p className="hint">{formatSeedResult(lastSeedResult)}</p>
        </div>

        <div className="campaign-seed-tools">
          <p className="panel-label">Uplink Sync</p>
          <div className="console-actions">
            <button disabled={loadingShell || loadingCampaigns} onClick={() => onRefreshShell()} type="button">
              {loadingShell || loadingCampaigns ? "Refreshing..." : "Refresh shell"}
            </button>
            <button
              disabled={!selectedCampaignId || loadingState}
              onClick={() => onRefreshActiveCampaign(selectedCampaignId)}
              type="button"
            >
              {loadingState ? "Refreshing..." : "Refresh active campaign"}
            </button>
          </div>
          <p className="hint">
            Provider: {shellReadiness.provider.label}. Canon frame: {shellReadiness.campaignSeed.label}.
          </p>
        </div>
      </div>
    </section>
  );
}
