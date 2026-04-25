export function PlayerInput({ disabled, isSubmitting, onSubmit, onValueChange, placeholder, value }) {
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
      <label className="panel-label" htmlFor="player-input">
        Your move
      </label>
      <textarea
        disabled={disabled || isSubmitting}
        id="player-input"
        onChange={(event) => onValueChange(event.target.value)}
        placeholder={placeholder}
        rows={4}
        value={value}
      />
      <div className="input-actions">
        <span className="hint">
          {disabled
            ? "Load a campaign before transmitting actions to the GM."
            : "Player-safe output only. Hidden state remains server-side."}
        </span>
        <button disabled={disabled || isSubmitting || !value.trim()} type="submit">
          {isSubmitting ? "Transmitting..." : "Send to GM"}
        </button>
      </div>
    </form>
  );
}
