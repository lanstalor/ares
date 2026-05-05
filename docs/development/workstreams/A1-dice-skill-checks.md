# Slice A1 — Dice + Skill Check Primitive

| Field | Value |
|---|---|
| **Track** | A — Mechanical Depth |
| **Branch** | `track-a/A1-dice-skill-checks` |
| **Worktree** | `~/ares-track-a/A1` |
| **PR** | https://github.com/lanstalor/ares/pull/10 (draft) |
| **Status** | in-flight (12/12 tasks complete; Docker smoke/screenshot pending) |
| **Last agent** | Codex (2026-05-05) |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |
| **Implementation plan** | `docs/superpowers/plans/2026-05-05-A1-dice-skill-checks.md` |

---

## Goal

Add a Red Rising-flavored skill-check primitive so the GM can call for and resolve attribute checks (Strength, Cunning, Will, Charm, Tech) and the player sees the dice in the turn feed. Gated behind `ARES_ENABLE_DICE` (default off).

## Last-known-good commit

`HEAD` — `feat(A1): complete dice roll response path`

Test status at this commit:
- backend (`PYTHONPATH=backend /home/lans/ares/backend/.venv/bin/pytest backend/tests -q`): ✅ 85 passing
- frontend (`make check`): ✅ compileall + node syntax checks passed
- frontend (`npm run build`): ✅ passed after rebasing onto `origin/main` with PR #12 merged.
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run (requires resolving frontend build/runtime blocker first)

## In-flight WIP

`clean after commit` — all implementation tasks are complete. Remaining work is Docker/5180 dice smoke with `ARES_ENABLE_DICE=true` and screenshot capture.

## Files touched so far

- ✅ `backend/app/core/config.py` — `enable_dice: bool` setting added
- ✅ `backend/app/services/ai_provider.py` — `Roll` dataclass + `rolls` field on `NarrationResponse`
- ✅ `backend/app/services/anthropic_provider.py` — `build_tool_schema()` builder + `_ROLLS_PROPERTY_SCHEMA` constant; `_build_response` translates `tool_input["rolls"]` into typed `Roll` instances; `AnthropicNarrationProvider.__init__` accepts `enable_dice`; `build_system_prompt()` conditionally appends dice guidance.
- ✅ `backend/app/services/provider_registry.py` — `get_narration_provider(..., *, enable_dice=False)` plumbed to Anthropic provider
- ✅ `backend/app/services/turn_engine.py` — passes `settings.enable_dice` through to `get_narration_provider`; `TurnEngineResult` carries rolls.
- ✅ `backend/app/api/routes/turns.py` — forwards rolls in `TurnResolution`.
- ✅ `backend/app/schemas/turn.py` — `rolls` added to `TurnResolution`.
- ✅ `backend/tests/test_a1_dice.py` — 15 tests covering settings, dataclass, schema builder, response parsing, provider wiring, prompt gating, engine propagation, and API forwarding.
- ✅ `frontend/src/App.jsx` — `buildConsequenceEvents` emits `system-roll`.
- ✅ `frontend/src/components/TurnFeed.jsx` — `system-roll` avatar.
- ✅ `frontend/src/styles.css` — `.turn-system-roll` amber/copper styling.

## Next concrete step

Do the Docker/5180 smoke with `ARES_ENABLE_DICE=true` and capture the dice screenshot.

## Open questions / blockers

- No code blockers. PR #12 merged into `main`, A1 was rebased onto it, and `npm run build` now passes.

## Agent rotation log

- 2026-05-05 — Claude → bootstrap + plan + Tasks 1–5 (settings flag, Roll dataclass, conditional tool schema, response translation, provider wiring). 81 tests passing. Ended at commit `aaaf504` due to imminent quota exhaustion. Working tree clean. Next: Task 6 (system-prompt addendum).
- 2026-05-05 — Codex → completed Tasks 6–12 (prompt addendum, backend/API roll propagation, frontend `system-roll` event/avatar/style). `PYTHONPATH=backend /home/lans/ares/backend/.venv/bin/pytest backend/tests -q` passed with 85 tests; `make check` passed. `npm run build` blocked by missing pre-existing `sceneArtLibrary.js`.
- 2026-05-05 — Codex → opened PR #12 for the missing scene-art library/assets and verified a temporary A1 + PR #12 merge: A1 focused tests passed, `make check` passed, `npm run build` passed.
- 2026-05-05 — Codex → merged PR #12 to `main`, rebased A1 onto updated `origin/main`, and verified `PYTHONPATH=backend /home/lans/ares/backend/.venv/bin/pytest backend/tests -q`, `make check`, and `npm run build` all pass on A1.

## How to resume (any agent)

```bash
cd ~/ares-track-a/A1
cat docs/development/workstreams/A1-dice-skill-checks.md     # this file
cat docs/superpowers/plans/2026-05-05-A1-dice-skill-checks.md  # the plan
git log --oneline -10
PYTHONPATH=backend /home/lans/ares/backend/.venv/bin/pytest backend/tests/ -q   # confirm 81 pass
```

Then resolve the scene-art library build blocker, rerun frontend build/smoke, and decide whether PR #10 can leave draft.

## Verification on completion

- [x] All 12 plan tasks complete
- [x] backend suite passes
- [x] `make check` passes
- [ ] Playtester runs 30 turns clean with `ARES_ENABLE_DICE=false` (default) and `=true`
- [ ] Playwright screenshot at 5180 with dice enabled — save under `assets/samples/ui-iteration/2026-05-05-A1-dice-after.png`
- [ ] PR #10 marked ready for review (`gh pr ready 10`)

## Hard constraints checklist

- [x] Hidden state does not leak — rolls expose nothing the player wouldn't already see
- [x] Canon guard not bypassed — narration still passes through `evaluate_canon_guard`
- [x] Player character remains Davan of Tharsis
- [x] All AI calls go through `NarrationProvider` Protocol — confirmed
- [x] Stub provider works offline — confirmed (new tests use fake `messages_create`, no live API calls)
- [x] Default `ARES_ENABLE_DICE=false` keeps `main` behaviour identical — confirmed (full suite green with flag off)
