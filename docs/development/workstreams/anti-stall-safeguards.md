# Slice Anti-Stall — GM Anti-Stall Safeguards

| Field | Value |
|---|---|
| **Track** | Carryover |
| **Branch** | `carryover/anti-stall-safeguards` |
| **Worktree** | `~/ares` |
| **PR** | https://github.com/lanstalor/ares/pull/16 |
| **Status** | merged |
| **Last agent** | Codex |
| **Next agent** | any |
| **Parent plan** | `docs/development/master-plan.md` |

---

## Goal

Build structural scene-progression guardrails to track stall state and force the LLM GM to introduce a new fact, cost, or choice when a scene stalls, verified by improved playtester scores.

## Last-known-good commit

`d5a8a40` — `feat: chat quality, pacing, and memory slice (carryover/anti-stall-safeguards) (#16)`

Test status at this commit:
- backend (`make backend-test`): passed in merge validation
- frontend (`make check`): passed in merge validation
- playtester: initial 5-turn signal improved; later 20-turn report required a follow-up because the playtester prompts still used the old Davan/Lykos premise

## In-flight WIP

`merged` — PR #16 landed on `main`. A later Codex review found and patched two follow-up issues: canon-guard failures must not persist scene/combat summary state, and playtester prompts must use Mara/Relay 19 rather than Davan/Lykos before the next benchmark. The 2026-05-22 benchmark rerun produced a partial 9-turn report before OpenAI quota stopped backend GM calls and holistic evaluation.

## Files touched so far

- `backend/app/models/campaign.py` — ✅ Added stall_counter.
- `backend/alembic/versions/` — ✅ Generated and fixed migration.
- `backend/app/services/turn_engine.py` — ✅ Added consequence evaluation and counter logic.
- `backend/app/services/context_builder.py` — ✅ Added critical prompt injection when stall_counter >= 3.
- `backend/app/services/anthropic_provider.py` — ✅ Rewrote system prompt to explicitly ban static standoffs and tone down heavy sci-fi jargon.
- `backend/app/services/ai_provider.py` — ✅ Added scene_state and narrative_summary_update to NarrationResponse.
- `tools/playtester/player.py` — ✅ Retargeted player simulation to Mara of Cimmeria / Relay 19 in the follow-up pass.
- `tools/playtester/evaluator.py` — ✅ Retargeted evaluator context to Mara of Cimmeria / Relay 19 in the follow-up pass.

## Next concrete step

Restore provider quota or switch providers, then rerun the 20-turn playtester with Mara/Relay 19 prompts and compare against `tools/playtester/reports/2026-05-13-01-10.md`. Treat the older report's evaluator scores as suspect because its evaluator prompt referenced Davan/Lykos. Partial rerun evidence is in `tools/playtester/reports/2026-05-22-00-24.md`.

## Open questions / blockers

- OpenAI quota stopped the 2026-05-22 rerun after 9 scored turns.

## Agent rotation log

- `2026-05-11 UTC` — Gemini → Bootstrapped slice, created branch, updated master plan, and set up workstream doc.
- `2026-05-11 UTC` — Gemini → Implemented stall_counter logic, rewrote GM system prompt to fix static standoffs and jargon, and swapped local `.env` model to `gpt-5.5`. Interim push before handoff.
- `2026-05-12 UTC` — Claude/Codex → Expanded into chat quality, pacing, scene-state memory, and narrative summary. Merged via PR #16.
- `2026-05-22 UTC` — Codex → Reviewed latest repo state, found canon-guard state persistence and stale playtester premise, patched both, and refreshed handoff docs for abrupt session continuation.
- `2026-05-22 UTC` — Codex → Hardened playtester provider error handling and ran `ARES_PLAYTESTER_TURNS=20 python3 tools/playtester/run.py`; report stopped at 9 scored turns due OpenAI quota, saved as `tools/playtester/reports/2026-05-22-00-24.md`.

## Verification on completion

Before marking this slice **review**:

- [x] `make backend-test` passes
- [x] `make check` passes
- [ ] Full 20-turn playtester rerun with Mara/Relay 19 prompts
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [x] Workstream doc fully reflects final state
- [x] PR description summarized the slice
- [x] `CLAUDE.md` updated for current state

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Current player-character constraint remains documented for this branch
- [x] All AI/media/TTS calls go through a Provider Protocol
- [x] Stub provider works offline (no API key required for `make backend-test`)
