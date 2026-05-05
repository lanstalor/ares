export function ActionBar({ actions = [], disabled, onSelectAction, sceneTone }) {
  const visibleActions = actions.slice(0, 4);

  return (
    <div className={`action-tab-strip tone-${sceneTone}`} aria-label="Suggested actions">
      {visibleActions.map((action, index) => (
        <button
          className="action-tab"
          disabled={disabled}
          key={action.id}
          onClick={() => onSelectAction(action.prompt)}
          type="button"
        >
          <span className="action-tab-key">{action.key ?? index + 1}</span>
          <span className="action-tab-label">{action.label}</span>
        </button>
      ))}
    </div>
  );
}
