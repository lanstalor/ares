import React from "react";

/**
 * Renders the live combat panel when campaign.combat_state.active is true.
 * Shows round counter, initiative order with HP bars (from scene_participants),
 * defeated state, and the most recent damage line.
 */
export function CombatPanel({ combatState, participants = [] }) {
  if (!combatState || !combatState.active) {
    return null;
  }

  const participantByName = new Map(participants.map((p) => [p.name, p]));

  return (
    <section className="combat-panel" aria-label="Combat panel">
      <header className="combat-panel-header">
        <span className="combat-panel-badge">⚔ COMBAT</span>
        <span className="combat-panel-round">Round {combatState.round ?? 1}</span>
      </header>

      <ol className="combat-initiative">
        {(combatState.initiative_order ?? []).map((entry) => {
          const live = participantByName.get(entry.name);
          const hp = live?.current_hp;
          const maxHp = live?.max_hp;
          const hpPct = hp != null && maxHp ? Math.max(0, Math.min(100, (hp / maxHp) * 100)) : null;
          return (
            <li
              key={entry.name}
              className={[
                "combat-initiative-row",
                entry.is_player ? "is-player" : "",
                entry.defeated ? "is-defeated" : "",
              ].filter(Boolean).join(" ")}
            >
              <span className="combat-initiative-name">{entry.name}</span>
              <span className="combat-initiative-score">init {entry.initiative_score}</span>
              {hpPct != null ? (
                <span className="combat-initiative-hp" aria-label={`HP ${hp} of ${maxHp}`}>
                  <span
                    className="combat-initiative-hp-fill"
                    style={{ width: `${hpPct}%` }}
                  />
                </span>
              ) : null}
              {entry.defeated ? <span className="combat-initiative-defeated">DOWN</span> : null}
            </li>
          );
        })}
      </ol>

      {combatState.last_damage ? (
        <p className="combat-last-damage">{combatState.last_damage}</p>
      ) : null}
    </section>
  );
}
