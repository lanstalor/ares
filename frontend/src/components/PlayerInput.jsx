import { ActionBar } from "./ActionBar";

export function PlayerInput({
  actions,
  disabled,
  isSubmitting,
  onSelectAction,
  onSubmit,
  onValueChange,
  placeholder,
  sceneTone,
  value,
}) {
  const handleSubmit = (event) => {
    event.preventDefault();
    if (disabled || isSubmitting) return;

    const nextValue = value.trim();
    if (!nextValue) return;

    onSubmit(nextValue);
    onValueChange("");
  };

  return (
    <form className="input-panel" onSubmit={handleSubmit}>
      <div className="input-terminal-bar">
        <label className="panel-label" htmlFor="player-input">
          Command line
        </label>
        <span className="hint">
          {disabled
            ? "Campaign link required."
            : "Secure relay. Hidden state remains server-side."}
        </span>
      </div>
      <div className="command-row">
        <ActionBar
          actions={actions}
          disabled={disabled}
          onSelectAction={onSelectAction}
          sceneTone={sceneTone}
        />
        <textarea
          disabled={disabled || isSubmitting}
          id="player-input"
          onChange={(event) => onValueChange(event.target.value)}
          placeholder={placeholder}
          rows={1}
          value={value}
        />
        <button disabled={disabled || isSubmitting || !value.trim()} type="submit">
          {isSubmitting ? "Transmitting..." : "Execute"}
        </button>
      </div>
    </form>
  );
}
