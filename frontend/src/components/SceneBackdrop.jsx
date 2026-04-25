export function SceneBackdrop({ currentLocation, objective, sceneTone, selectedCampaign }) {
  return (
    <section className={`scene-backdrop-panel tone-${sceneTone}`}>
      <div className="scene-backdrop-art">
        <div className="scene-grid" />
        <div className="scene-planet" />
        <div className="scene-ring" />
        <div className="scene-cityline" />
        <div className="scene-lights" />
        <div className="scene-sigil">ARES</div>
        <div className="scene-horizon" />
      </div>

      <div className="scene-backdrop-copy">
        <p className="eyebrow">Environment</p>
        <h2>{currentLocation ?? "Crescent Block / Callisto Depot District"}</h2>
        <p>
          {selectedCampaign?.tagline ??
            "Atmospheric placeholder backdrop. Replace with painted environment art once the scene asset pipeline lands."}
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
    </section>
  );
}
