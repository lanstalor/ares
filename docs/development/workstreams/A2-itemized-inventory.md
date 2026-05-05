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

`51a7974` — `feat(A2): create Item model, Alembic migration, and operator schemas`

Test status at this commit:
- backend (`make backend-test`): ✅ 98 passed
- frontend (`make check`): ✅
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run

## In-flight WIP

- `wip 51a7974` — Item model and DB migration are complete. Next is updating the GM context.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/A2-itemized-inventory.md` — updated ⚠️
- `backend/app/models/character.py` — Added `Item` model ✅
- `backend/app/models/campaign.py` — Added `items` relationship ✅
- `backend/alembic/versions/05561cace318_add_items_table.py` — Migration generated ✅
- `backend/app/schemas/character.py` — Added `ItemRead` and updated `CharacterRead` ✅
- `backend/app/schemas/operator.py` — Added `ItemUpdate` to patch schemas ✅
- `backend/app/api/routes/operator.py` — Handled items in state repair ✅

## Next concrete step

Update `backend/app/services/context_builder.py` to include the character's items in the GM's system prompt context (e.g., formatting them under an "INVENTORY" section). Then update `AnthropicNarrationProvider` to include an `inventory_updates` array in the `_TOOL_SCHEMA` so the GM can add/remove items as a consequence.

## Open questions / blockers

- ...

## Agent rotation log

Append-only. One line per session.

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
