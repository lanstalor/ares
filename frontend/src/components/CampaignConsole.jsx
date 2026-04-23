export function CampaignConsole({
  campaigns,
  createForm,
  creatingCampaign,
  loadingCampaigns,
  onSeedWorldBible,
  onCreateCampaign,
  onFormChange,
  onSelectCampaign,
  seedingWorldBible,
  selectedCampaignId,
  worldBibleReady,
}) {
  return (
    <section className="status-panel">
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Campaign Console</p>
          <h2>Operations</h2>
        </div>
        <span className="panel-chip">{loadingCampaigns ? "Syncing" : `${campaigns.length} loaded`}</span>
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
              No campaigns found. Create the first active cell to start the turn loop.
            </p>
          )}
        </div>

        <form className="campaign-form" onSubmit={onCreateCampaign}>
          <label className="panel-label" htmlFor="campaign-name">
            New campaign
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
            {creatingCampaign ? "Creating..." : "Create campaign"}
          </button>
        </form>

        <div className="campaign-seed-tools">
          <p className="panel-label">Canonical bootstrap</p>
          <p className="hint">
            {worldBibleReady
              ? "Seed a campaign directly from world_bible.md."
              : "Backend cannot see world_bible.md yet."}
          </p>
          <button
            disabled={seedingWorldBible || !worldBibleReady}
            onClick={onSeedWorldBible}
            type="button"
          >
            {seedingWorldBible ? "Seeding..." : "Seed from world bible"}
          </button>
        </div>
      </div>
    </section>
  );
}
