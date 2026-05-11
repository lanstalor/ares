# Slice FG3 — Playtest Blockers

| Field | Value |
|---|---|
| **Track** | Focus Group |
| **Branch** | `focus-group/new-protagonist-intro` |
| **Worktree** | `~/ares` |
| **PR** | https://github.com/lanstalor/ares/pull/15 |
| **Status** | review |
| **Last agent** | Codex |
| **Next agent** | Gemini CLI or Claude Code |
| **Parent plan** | `docs/development/human-in-the-loop-ux-testing-process.md` |

---

## Goal

Patch the tester-blocking FG1/FG2 findings before focus-group testing: stop `context_excerpt` hidden-state leakage, replace generic opening actions, and remove the pre-Darrow `Howler` role label from the active player-facing build.

## Last-known-good commit

`174cdd1` — `fix(FG3): patch playtest blockers`

Verification at this commit:
- `backend/.venv/bin/pytest backend/tests/test_turn_api_contract.py backend/tests/test_world_bible_parser.py`: passed, 7 tests
- `make backend-test`: passed, 225 tests
- `make check`: passed
- `npm run build`: passed in `frontend/`
- `docker compose up --build -d`: passed
- Docker API smoke: fresh campaign `26a677f7-592f-4ab6-b435-758713b26511`, hidden `ident_flagged` injected, `POST /turns` returned 201 without `ident_flagged`, `Active conditions`, `Active clocks`, `[GM-only context`, or `Opening pressure clocks`
- Playwright smoke at 1366x1024: first action buttons before a submitted turn were `Run Cold Pull`, `Loop Suit Cam`, `Ask Oran`, and `Fake Coupling Report`
- LAN load smoke: `http://192.168.3.233:5180/?intro=1` returned 200

## In-flight WIP

`clean after commit` — blocker patch complete and ready for the First Meaningful Turn HITL pass.

## Files touched so far

- `backend/app/api/routes/turns.py` — `TurnResolution.context_excerpt` remains present but now returns only the player-safe summary/fallback from `POST /turns`.
- `backend/tests/test_turn_api_contract.py` — regression coverage proves hidden `ident_flagged`, active-condition labels, hidden-clock labels, and GM-only brief markers do not appear in a player turn response.
- `frontend/src/lib/uiTheme.js` — Relay 19 opening fallback actions now use scene-specific buttons and prompts before the first submitted turn.
- `frontend/src/App.jsx` — passes campaign/location context into fallback action selection.
- `world_bible.md` — active HighRed player role renamed to `Guerrilla Technician`.
- `backend/app/api/routes/campaigns.py` — bootstrap fallback uses `Guerrilla Technician`.
- `frontend/src/lib/devUiFixture.js` — dev fixture uses `Guerrilla Technician`.
- `backend/tests/test_world_bible_parser.py` — parser test asserts the new class label.
- `docs/development/focus-group/FG1-hitl-smoke-and-test-plan-2026-05-09.md` — smoke notes use the new role label.

## Tester Findings Already Handled

- `context_excerpt` no longer echoes raw turn context from `POST /turns`.
- Hidden `ident_flagged` remains available to backend/operator flows but is absent from player turn responses.
- Opening action buttons are no longer generic `Talk / Bribe / Shadow / Inspect` in the Relay 19 opening.
- Mara is no longer labeled `Howler (Guerrilla subclass)` in the active world seed, backend fallback, dev fixture, or focus-group smoke docs.

## Deferred Playtest Follow-ups

- Objective/inventory consistency after extracting the ghost packet.
- Player-safe pressure feedback when hidden clocks advance.
- Relay 19 scene-art fallback quality.
- Operator/dev language cleanup such as `LLM GM live` and `Hidden state remains server-side`.

## Current Docker URLs

- Host: `http://localhost:5180/?intro=1`
- LAN: `http://192.168.3.233:5180/?intro=1`

## Next concrete step

Run the FG1 Intro Scenario plus First Meaningful Turn HITL pass from PR #15 with a human player. Log notes under `docs/development/ux-tests/`.

## Open questions / blockers

- No current blocker.
- The Playwright smoke saw only the existing missing `favicon.ico` 404 in the console.

## Gemini CLI Resume Prompt

```text
Continue work in /home/lans/ares.

Read in this order:
1. GEMINI.md or CLAUDE.md
2. docs/development/agent-handoff-protocol.md
3. docs/development/master-plan.md
4. docs/development/workstreams/FG3-playtest-blockers.md

Use branch focus-group/new-protagonist-intro and PR #15:
https://github.com/lanstalor/ares/pull/15

Latest blocker patch commit: 174cdd1.
Current Docker URLs:
- host: http://localhost:5180/?intro=1
- LAN: http://192.168.3.233:5180/?intro=1

Run the FG1 Intro Scenario plus First Meaningful Turn HITL pass with a human player.
Log notes under docs/development/ux-tests/.
Before stopping, update this workstream doc, commit, and push.
```

## Claude Code Resume Prompt

```text
Continue work in /home/lans/ares.

Read in this order:
1. CLAUDE.md
2. docs/development/agent-handoff-protocol.md
3. docs/development/master-plan.md
4. docs/development/workstreams/FG3-playtest-blockers.md

Use branch focus-group/new-protagonist-intro and PR #15:
https://github.com/lanstalor/ares/pull/15

Latest blocker patch commit: 174cdd1.
Current Docker URLs:
- host: http://localhost:5180/?intro=1
- LAN: http://192.168.3.233:5180/?intro=1

Run the FG1 Intro Scenario plus First Meaningful Turn HITL pass with a human player.
Log notes under docs/development/ux-tests/.
Before stopping, update this workstream doc, commit, and push.
```

## Agent rotation log

- `2026-05-11 UTC` — Codex created `groom/fg3-playtest-blockers`, patched the playtest blockers, verified backend/frontend/Docker/Playwright smoke, and prepared Gemini/Claude handoff for PR #15.

## Verification on completion

- [x] `make backend-test` passes
- [x] `make check` passes
- [x] `npm run build` passes
- [x] Docker stack rebuilds
- [x] Docker API leak smoke passes with hidden `ident_flagged`
- [x] Playwright confirms Relay 19 first-action buttons
- [x] LAN focus-group URL loads
- [x] Workstream doc fully reflects final state
- [x] Branch pushed for handoff

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Red Rising canon/factions/Color rules remain intact
- [x] Focus-group player character remains Mara of Cimmeria
- [x] All AI/media calls go through Provider Protocols or documented generation tooling
- [x] Stub provider works offline
