import { useState } from "react";

export function ActionBar({ actions, disabled, onSelectAction, sceneTone }) {
  const [open, setOpen] = useState(false);

  const handleSelectAction = (prompt) => {
    onSelectAction(prompt);
    setOpen(false);
  };

  return (
    <div className={`quick-ops-control tone-${sceneTone} ${open ? "is-open" : ""}`}>
      <div className="quick-ops-terminal">
        <button
          aria-expanded={open}
          aria-label="Show action ideas"
          className="quick-ops-trigger"
          disabled={disabled}
          onClick={() => setOpen((current) => !current)}
          type="button"
        >
          <span className="idea-bulb" aria-hidden="true" />
        </button>
      </div>

      <div className="action-grid" hidden={!open}>
        {actions.map((action) => (
          <button
            className="action-button"
            disabled={disabled}
            key={action.id}
            onClick={() => handleSelectAction(action.prompt)}
            type="button"
          >
            <span className="action-index">{action.key}</span>
            <span className="action-icon">{action.icon}</span>
            <span className="action-label">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
