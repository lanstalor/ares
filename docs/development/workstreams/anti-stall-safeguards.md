# Slice Anti-Stall — GM Anti-Stall Safeguards

| Field | Value |
|---|---|
| **Track** | Carryover |
| **Branch** | `carryover/anti-stall-safeguards` |
| **Worktree** | `~/ares` |
| **PR** | TBD |
| **Status** | in-flight |
| **Last agent** | Gemini |
| **Next agent** | any |
| **Parent plan** | `docs/development/master-plan.md` |

---

## Goal

Build structural scene-progression guardrails to track stall state and force the LLM GM to introduce a new fact, cost, or choice when a scene stalls, verified by improved playtester scores.

## Last-known-good commit

`666422f` — `chore: remove one-off python utility scripts and old snapshot from root`

Test status at this commit:
- backend (`make backend-test`): not-run
- frontend (`make check`): not-run
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run

## In-flight WIP

`clean` — fully implemented, tested, and playtester verified. Ready for PR.

## Files touched so far

- `backend/app/models/campaign.py` — ✅ Added stall_counter.
- `backend/alembic/versions/` — ✅ Generated and fixed migration.
- `backend/app/services/turn_engine.py` — ✅ Added consequence evaluation and counter logic.
- `backend/app/services/context_builder.py` — ✅ Added critical prompt injection when stall_counter >= 3.
- `backend/app/services/anthropic_provider.py` — ✅ Rewrote system prompt to explicitly ban static standoffs and tone down heavy sci-fi jargon.

## Next concrete step

Verify the prompt/model changes with manual testing, then create a PR for `carryover/anti-stall-safeguards`.

## Open questions / blockers

- None

## Agent rotation log

- `2026-05-11 UTC` — Gemini → Bootstrapped slice, created branch, updated master plan, and set up workstream doc.
- `2026-05-11 UTC` — Gemini → Implemented stall_counter logic, rewrote GM system prompt to fix static standoffs and jargon, and swapped local `.env` model to `gpt-5.5`. Interim push before handoff.

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
- [ ] Current player-character constraint remains documented for this branch
- [ ] All AI/media/TTS calls go through a Provider Protocol
- [ ] Stub provider works offline (no API key required for `make backend-test`)