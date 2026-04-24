import { useState } from "react";

export function PlayerInput({ disabled, isSubmitting, onSubmit, placeholder }) {
  const [value, setValue] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (disabled || isSubmitting) return;

    const nextValue = value.trim();
    if (!nextValue) return;

    onSubmit(nextValue);
    setValue("");
  };

  return (
    <form className="input-panel" onSubmit={handleSubmit}>
      <label className="panel-label" htmlFor="player-input">
        Action
      </label>
      <textarea
        disabled={disabled || isSubmitting}
        id="player-input"
        onChange={(event) => setValue(event.target.value)}
        placeholder={placeholder}
        rows={4}
        value={value}
      />
      <div className="input-actions">
        <span className="hint">
          {disabled
            ? "Select or create a campaign to begin."
            : "Player-safe output only. Hidden state stays server-side."}
        </span>
        <button disabled={disabled || isSubmitting || !value.trim()} type="submit">
          {isSubmitting ? "Transmitting..." : "Transmit"}
        </button>
      </div>
    </form>
  );
}
