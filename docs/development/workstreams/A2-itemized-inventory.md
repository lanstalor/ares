# Slice A2 — Itemized Inventory

> Template — copy to `{slice-id}-itemized-inventory.md` and fill in. `make bootstrap-slice SLICE=A2` does this automatically.

| Field | Value |
|---|---|
| **Track** | A |
| **Branch** | `track-a/A2-itemized-inventory` |
| **Worktree** | `~/ares-track-a/A2` |
| **PR** | TBD |
| **Status** | in-flight |
| **Last agent** | Gemini |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Transition from a flat `inventory_summary` string to a structured `Item` model, allowing characters to own, acquire, and lose specific items with mechanical properties (tags, weight, rarity). Update the GM engine to use these items for narrative leverage and consequence application.

## Last-known-good commit

`HEAD` — `chore(A2): bootstrap slice — branch + workstream doc`

Test status at this commit:
- backend (`make backend-test`): ✅
- frontend (`make check`): ✅
- playtester (offline, stub provider): ✅
- playwright screenshot at 5180: ✅

## In-flight WIP

- `clean` — no uncommitted edits, last commit is a `chore:`.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/A2-itemized-inventory.md` — initialized ✅

## Next concrete step

Create `backend/app/models/item.py` defining the `Item` model (linked to `Character` and `Campaign`) and generate the Alembic migration to add the `items` table.

## Open questions / blockers

- ...

## Agent rotation log

Append-only. One line per session.

- `YYYY-MM-DD HH:MM UTC` — Agent → what was done; status at end of session
- ...

## Verification on completion

Before marking this slice **review**:

- [ ] `make backend-test` passes
- [ ] `make check` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [ ] Workstream doc fully reflects final state
- [ ] Draft PR description summarizes the slice
- [ ] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [ ] Hidden state does not leak to player
- [ ] Canon guard not bypassed
- [ ] Player character remains Davan of Tharsis
- [ ] All AI/media/TTS calls go through a Provider Protocol
- [ ] Stub provider works offline (no API key required for `make backend-test`)
