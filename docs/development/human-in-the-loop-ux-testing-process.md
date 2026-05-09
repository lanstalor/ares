# Human-In-The-Loop UX Testing Process

## Purpose

Run structured human play sessions that expose immersion breaks, confusing UI states, pacing stalls, and hidden-state leaks before adding more feature slices. This process complements automated playtester reports; it does not replace backend tests or Playwright screenshots.

## Roles

- **Player:** Uses only the player-facing app. On the host machine this is `http://localhost:5180/`; from another LAN device use the host LAN address, for example `http://192.168.3.233:5180/`. Thinks aloud, but does not inspect admin state or logs.
- **Facilitator:** Watches the player, asks neutral prompts, timestamps issues, and avoids explaining the system unless the player is blocked.
- **Operator:** Uses `/admin`, backend logs, and DB/API checks only between turns or after a scenario. Does not coach the player.
- **Recorder:** Captures notes, screenshots, and issue IDs. This can be the facilitator for small sessions.

For early Ares testing, one person can play Player and one person can combine Facilitator/Operator/Recorder.

## Environment Setup

1. Start from a clean checkpoint branch or a named grooming branch.
2. Ensure `.env` has:
   - `ARES_GENERATION_PROVIDER=stub` for deterministic UI workflow tests, or the intended live provider for narrative tests.
   - `ARES_MEDIA_PROVIDER=stub` unless media generation is explicitly under test.
   - `ARES_OPERATOR_TOKEN=<local test token>` for `/admin`.
3. Run:
   - `make check`
   - `make backend-test`
   - `make frontend-build`
   - `make compose-up`
4. Open the player URL (`http://localhost:5180/` on the host, or `http://<host-lan-ip>:5180/` from another LAN device) and set `localStorage.ares_intro_seen=1` when the intro is not under test.
5. Open `/admin` in a separate browser profile or private window so operator state cannot affect the player session.

## Session Structure

Each session is 45-75 minutes:

1. **Baseline check, 5 minutes**
   - Confirm app loads.
   - Confirm player can identify current objective, location, character status, and command input.
   - Confirm operator can view full state with token.
2. **Scenario pass, 30-45 minutes**
   - Run 2-4 scenario scripts below.
   - Player thinks aloud.
   - Facilitator records friction without correcting it.
3. **Debrief, 10-15 minutes**
   - Player names the most confusing moment, most immersive moment, and one thing they expected but could not do.
   - Operator compares player perception against backend state.
4. **Triage, 10 minutes**
   - Convert findings into issues or grooming tasks.
   - Assign severity and owner track.

## Scenario Scripts

### FG1 Intro Scenario: Relay 19 Opening

Goal: verify that the restored intro and new protagonist establish the premise without facilitator explanation.

Player prompt:

> Start from the title screen. Watch the intro, enter the campaign, identify who you are, where you are, what is urgent, and take the first action that feels right.

Start at `http://<host-lan-ip>:5180/?intro=1` from another LAN device, or `http://localhost:5180/?intro=1` on the host, so prior browser state cannot skip the intro. Current host LAN URL for FG1 is `http://192.168.3.233:5180/?intro=1`.

Observe:

- Does "Mara of Cimmeria" read as a Red protagonist quickly?
- Does Relay 19 feel like a concrete starting zone rather than abstract lore?
- Does the player understand the ghost packet, the timer, and the Gray surveillance pressure?
- Does the intro art support the scene instead of feeling like unrelated decoration?
- Does the first objective give the player an obvious verb: pull, hide, reroute, distract, or run?

### Scenario 1: First Meaningful Turn

Goal: verify onboarding into play without the facilitator explaining the system.

Player prompt:

> You have just entered the game. Find your current goal, inspect what matters, and take the first action that feels right.

Observe:

- Can the player find the active objective?
- Do suggested actions help or feel generic?
- Does the scene art reinforce the text?
- Does the player understand what the command input expects?

### Scenario 2: Pressure And Consequence

Goal: verify that visible mechanics feel connected to fiction.

Player prompt:

> Push a risky action: lie, sneak, threaten, force a door, inspect suspicious gear, or resist an NPC.

Observe:

- Does the GM create cost, choice, or changed leverage?
- Are dice, clocks, inventory, secrets, or conditions visible when they matter?
- Does the player understand what changed after the turn?
- Does the UI highlight consequences without leaking hidden state?

### Scenario 3: Scene Stall Probe

Goal: expose repeated scene beats and weak progression.

Player prompt:

> Stay in the same confrontation for several turns. Be cautious, negotiate, delay, or ask clarifying questions.

Observe:

- Does each turn add a new fact, cost, choice, participant movement, or clock pressure?
- Does the GM repeat posture, ambient details, or threats?
- Does the player feel stuck because the system is waiting for a specific verb?
- Do suggested actions break the loop or reinforce it?

### Scenario 4: Operator Repair

Goal: verify operator tools support recovery without disrupting player immersion.

Operator task:

> During or after play, edit one objective, one clock, and one NPC field in `/admin`, then return to the player shell and continue.

Observe:

- Does token gating work?
- Can the operator target the correct campaign?
- Does the player-facing shell reflect safe updates clearly?
- Are hidden fields protected from the player surface?

### Scenario 5: Mobile Readability

Goal: verify the shell remains playable on phone-sized screens.

Viewport: `390x844`.

Observe:

- Can the player read the latest GM response and submit a command?
- Are participant chips, conditions, popouts, and action buttons usable?
- Does any text overflow or overlap?
- Is the primary play loop accessible without hunting through panels?

## Observation Rubric

Score each category 1-5 after every scenario:

| Category | 1 | 3 | 5 |
|---|---|---|---|
| Orientation | Player cannot tell what is happening | Player can proceed with effort | Player knows location, goal, and options |
| Agency | Player feels trapped or railroaded | Some useful choices | Choices feel distinct and consequential |
| Consequence Clarity | State changes are invisible or confusing | Some changes clear | Fiction and UI both show what changed |
| Immersion | UI/system breaks fiction often | Mixed | UI reinforces fiction without hiding controls |
| Flow | Scene stalls or repeats | Partial movement | Each turn changes the situation |
| Trust | Player doubts state consistency | Some uncertainty | Player believes the world remembers correctly |

Severity:

- **Critical:** hidden-state leak, admin bypass, blocked play loop, or player cannot continue.
- **High:** repeated immersion break, misleading UI, stale/wrong state, or consequence not visible.
- **Medium:** confusing copy, weak affordance, missing feedback, or mobile friction.
- **Low:** polish, wording, layout refinement, or nice-to-have enhancement.

## Evidence Capture

For every issue, record:

- Branch and commit SHA.
- Provider mode and model.
- Scenario number.
- Turn number or timestamp.
- Player action.
- Expected result.
- Actual result.
- Screenshot path, if visual.
- Backend/API evidence, if state-related.
- Severity and proposed owner track.

Store screenshots under:

`assets/samples/ui-iteration/{date}-hitl-{scenario}-{short-label}.png`

Store notes under:

`docs/development/ux-tests/{date}-{branch}.md`

## Issue Template

```md
## Finding

- Severity:
- Scenario:
- Branch / SHA:
- Provider:
- Turn / timestamp:
- Player action:
- Expected:
- Actual:
- Evidence:
- Suspected subsystem:
- Recommended fix:
```

## Exit Criteria

A grooming pass is ready to close when:

- No Critical findings remain open.
- High findings have an owner branch or explicit deferral.
- At least one desktop and one mobile scenario pass were completed.
- The operator can access `/admin` only with a valid token.
- A player can complete three consecutive turns without facilitator explanation.
- The latest HITL notes are linked from the relevant workstream doc.

## Recommended Cadence

- Run a short HITL smoke after each grooming branch.
- Run a full HITL pass before starting A4 combat mode.
- Repeat the full pass after A4, B4, and C3 are integrated, because combat, TTS, and lore authoring will all change player trust and pacing.
