# FG1 HITL Smoke And Test Plan — 2026-05-09

## Scope

Validate the FG1 focus-group branch before human testing:

- Branch: `focus-group/new-protagonist-intro`
- Draft PR: https://github.com/lanstalor/ares/pull/15
- Campaign premise: Mara of Cimmeria, HighRed surface relay technician, Surface Relay Tower 19, ghost-packet opening.
- Canon frame: Red Rising, 728 PCE, Ganymede, Sons of Ares era.

## Docker Smoke Result

Status: passed.

Commands / checks:

- `docker compose up --build -d`
- `curl http://localhost:8000/api/v1/health`
- `curl http://localhost:8000/api/v1/system/status`
- `POST /api/v1/seed/world-bible`
- `GET /api/v1/campaigns/{campaign_id}/state`
- Playwright title-screen smoke at `http://localhost:5180/`
- LAN reachability check at `http://192.168.3.233:5180/?intro=1`

Seeded smoke campaign:

- Campaign ID: `148bf7fa-8f5f-48ce-8fa3-c43eb03543fc`
- Campaign name: `FG1 Docker Smoke 2026-05-09`
- Player: `Mara of Cimmeria`
- Race/class: `HighRed`, `Howler (Guerrilla subclass)`
- Location: `Surface Relay Tower 19`
- Objective: `Recover the ghost packet from Relay 19`
- HP / cover: `40/40`, cover integrity `8`

Visual evidence:

- `assets/samples/ui-iteration/2026-05-09-FG1-docker-title-desktop.png`

Notes:

- Backend health returned `{"status":"ok"}`.
- Frontend title screen showed `Uplink connected`.
- `scene_art` was `null` on the seeded state, so the frontend used fallback/local art. This is acceptable for FG1 because intro art is bundled and scene art generation remains provider/cache-driven.

## Human-In-The-Loop Scenario

Run with one player and one facilitator/operator.

Start URL:

> `http://192.168.3.233:5180/?intro=1`

This forces the intro even if the browser has already set `localStorage.ares_intro_seen=1` from a previous run.

Player prompt:

> Start from the title screen. Watch the intro, enter the campaign, identify who you are, where you are, what is urgent, and take the first action that feels right.

Observe:

- Can the player tell they are Mara, a Red, and a surface relay technician?
- Can the player explain Relay 19 in one sentence?
- Does the ghost-packet timer create clear urgency?
- Does Gray surveillance read as immediate pressure?
- Does the player know what the command input expects?
- Are the suggested actions useful or generic?
- Does the intro feel like it belongs to the playable scene?

## Findings Log

Use this section during the human session.

| Time | Surface | Observation | Severity | Follow-up |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Exit Criteria

FG1 is ready to merge only after:

- At least one human completes the intro scenario.
- The player can state protagonist, location, urgent objective, and first action without facilitator explanation.
- Any severity-1 hidden-state leak, broken route, or first-turn blocker is fixed.
- Any severity-2 onboarding confusion is either fixed or explicitly accepted for the first focus group.
