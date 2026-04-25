export function ActionBar({ actions, disabled, onSelectAction, sceneTone }) {
  return (
    <section className={`action-bar tone-${sceneTone}`}>
      <div className="panel-chrome">
        <div>
          <p className="eyebrow">Action Bar</p>
          <h2>Decision Keys</h2>
        </div>
        <span className="panel-chip">{disabled ? "No campaign loaded" : `${actions.length} presets`}</span>
      </div>

      <div className="action-grid">
        {actions.map((action) => (
          <button
            className="action-button"
            disabled={disabled}
            key={action.id}
            onClick={() => onSelectAction(action.prompt)}
            type="button"
          >
            <span className="action-index">{action.key}</span>
            <span className="action-icon">{action.icon}</span>
            <span className="action-label">{action.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
