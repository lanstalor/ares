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

`16ec1f7` — `docs(A2): update workstream with DB and schema progress`

Test status at this commit:
- backend (`make backend-test`): ✅ 101 passed
- frontend (`make check`): ✅
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run

## In-flight WIP

- `clean` — Backend implementation is complete. Next is the frontend UI.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/A2-itemized-inventory.md` — updated ⚠️
- `backend/app/models/character.py` — Added `Item` model ✅
- `backend/app/models/campaign.py` — Added `items` relationship ✅
- `backend/alembic/versions/05561cace318_add_items_table.py` — Migration generated ✅
- `backend/app/schemas/character.py` — Added `ItemRead` and updated `CharacterRead` ✅
- `backend/app/schemas/operator.py` — Added `ItemUpdate` to patch schemas ✅
- `backend/app/api/routes/operator.py` — Handled items in state repair ✅
- `backend/app/services/context_builder.py` — Injected items into player-safe brief ✅
- `backend/app/services/ai_provider.py` — Added `InventoryUpdate` to `Consequences` ✅
- `backend/app/services/anthropic_provider.py` — Added `inventory_updates` to `_TOOL_SCHEMA` ✅
- `backend/app/services/consequence_applier.py` — Handled adding/removing/updating items ✅
- `backend/tests/test_a2_inventory.py` — Added test suite for inventory updates ✅

## Next concrete step

Update the frontend to display the character's items. We need to create an `InventoryPanel` (or update `StatusPanel`) to render the `ItemRead` objects returned from the backend, replacing the old flat `inventory_summary` text box. 

## Open questions / blockers

- ...

## Agent rotation log

Append-only. One line per session.

- `2026-05-06 00:05 UTC` — Gemini → Wired structured items into the GM's `context_builder.py` and updated `_TOOL_SCHEMA` so the GM can add/remove items. Added `test_a2_inventory.py`. All tests passing.
- `2026-05-05 23:55 UTC` — Gemini → Bootstrapped slice A2, created `Item` model, Alembic migration, and operator API schemas. Backend tests green. Next: wiring GM context.
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
