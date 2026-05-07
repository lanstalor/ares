# Codebase Snapshot — 2026-05-07

## Checkpoint

- Clean remote checkpoint: `main` at `c030cf7` (`checkpoint: clean main state before gameplay review`).
- Raw local safety checkpoint: `checkpoint/raw-main-2026-05-07` preserves the pre-cleanup `main` tip, including generated artifacts that were intentionally not pushed.
- Active review branch: `journey/2026-05-07-gameplay-ux-codebase-review`, created from `c030cf7`.
- `main` was pushed to `origin/main` after verification.

## Verification

Passed on clean checkpoint:

- `make check`
- `make backend-test` — `215 passed`
- `npm install` in `frontend` to restore missing declared dependencies
- `make frontend-build`

Frontend build originally failed because `react-router-dom` was declared in `package.json` and `package-lock.json`, but missing from installed `node_modules`. `npm install` resolved the local install state without tracked file changes.

## Repository Hygiene

The pre-cleanup local `main` had seven unpushed commits. One of them carried generated or local-only files such as `backend/venv`, backend egg-info, logs, and root-level screenshots. The cleaned checkpoint preserved only source, migrations, tests, and intended docs.

Remaining hygiene risks:

- Root-level screenshots and UI artifacts are already tracked in the repo from earlier work. Future visual evidence should live under `assets/samples/ui-iteration/`.
- `backend/app.db` and generated output appear in repo file inventories. Confirm whether each is intentionally tracked before the next release pass.
- The C2 worktree at `/home/lans/ares-track-c/C2` has unrelated dirty changes: deleted admin screenshots and a modified `docs/development/workstreams/C2-operator-app.md`. This was not touched during the checkpoint.

## Backend Findings

### Critical: Operator API Is Not Actually Token-Gated

The C2 admin frontend stores and sends `Authorization: Bearer {token}`, and the C2 spec requires token gating. The backend `operator.py` routes do not validate any token or depend on `ARES_OPERATOR_TOKEN`. This exposes full hidden state and patch access to any caller that can reach `/api/v1/operator/*`.

Recommended first fix:

- Add `ARES_OPERATOR_TOKEN` to settings.
- Add a FastAPI dependency that rejects missing or mismatched bearer tokens.
- Apply it to all operator routes, including `/operator/health` if that endpoint should not advertise the surface publicly.
- Add backend tests for no token, wrong token, and valid token.

### Critical: Live Provider Cannot Apply Conditions

`ConditionUpdate` exists in `consequence_applier.py`, and the turn engine processes condition consequences. The live narration tool schema and `_build_response()` do not expose or parse `condition_updates`, so real model turns cannot create bleeding/stunned/etc. through the provider path. Current tests cover service/fake-provider paths and participant display, but not the live tool contract.

Recommended first fix:

- Add `condition_updates` to the tool schema under `consequences`.
- Parse it into `ConditionUpdate` objects in `_build_response()`.
- Add Anthropic/OpenAI provider contract tests using a tool payload with `condition_updates`.

### High: Condition Ticking Removes One-Turn Conditions Immediately

The turn engine applies consequences, then processes all active conditions in the same turn. A new duration-1 condition is decremented and removed immediately. This may be intended for ephemeral effects, but it is a bad default for player-visible status effects because the player may never experience the state as persistent.

Recommended first fix:

- Decide whether newly applied conditions tick on the next turn boundary rather than the creation turn.
- Add tests for duration-1 and duration-2 player-facing behavior.

### High: Scene Context Uses Thin NPC Relevance

`context_builder.py` gathers scene NPCs by matching the current area faction. That is useful as a bootstrap heuristic, but weak for actual play: it can include irrelevant faction members and omit nearby actors, recurring NPCs, or characters established in recent turns.

Recommended first fix:

- Introduce a server-side scene presence model or current-scene participant table.
- Seed it from model output, recent turns, and operator state, then feed it back to context builder.
- Treat model-provided participants as hints until reconciled against known NPC/character records.

### Medium: Hard-Coded Known NPC Context Does Not Scale

The cleaned checkpoint includes a hard-coded Delta Sorin caste line in the player-safe context. It fixes an immediate dialogue/caste issue, but it is not a durable solution.

Recommended first fix:

- Move recurring-character caste and role knowledge into seeded world data or a relationship/context service.
- Generate the known-character brief from database state.

### Medium: Campaign Creation Swallows Bootstrap Failure

Campaign creation now attempts world-bible bootstrap and falls back to a scaffold character on exception. That keeps the UI usable, but a bootstrap failure can leave the player in a partial world with no obvious operator-facing warning.

Recommended first fix:

- Return or log a structured bootstrap status.
- Surface bootstrap degraded state in readiness/system status.
- Add an audit finding for campaigns created through fallback.

## Frontend Findings

### Critical: Admin Login Is Client-Only Without Backend Enforcement

The admin UI correctly sends a bearer token, but the backend ignores it. The UI may appear protected while hidden state remains exposed to direct API calls.

Recommended first fix: pair the backend operator-token dependency with admin tests that verify 401/403 behavior clears local storage and returns to login.

### High: Admin App Defaults To `test-campaign`

`AdminApp.jsx` derives `campaignId` from `fullState?.campaign_id || 'test-campaign'`, but `CampaignFullState` contains `campaign`, not `campaign_id`. On initial load, the admin tries to fetch a hard-coded campaign ID instead of letting the operator select a real campaign.

Recommended first fix:

- Add a campaign selector or route/query parameter for campaign ID.
- Derive campaign ID from `fullState.campaign.id` after load.
- Make the empty state explicit when no campaign ID is selected.

### High: Player Shell Persists Model Hints In Session Storage

Suggested actions and scene participants are stored in `sessionStorage`. This makes stale model hints durable across reloads and can make participants feel like canonical server state when they are not.

Recommended first fix:

- Store only per-campaign, per-turn hints with a turn ID.
- Clear hints on campaign switch and when no fresh response includes them.
- Prefer server-derived scene presence for participant strip state.

### Medium: Some UI Tabs Promise Systems That Are Not Real Yet

The SceneBackdrop has `Scene`, `Character`, `Inventory`, `Stats`, and `Map` tabs. Inventory and stats are partially real; map is still hard-coded preview content. This can break immersion because the UI implies dependable systems that do not yet exist.

Recommended first fix:

- Mark map as preview/disabled until B5.
- Enrich inventory with item descriptions and recent deltas.
- Show condition detail in stats/character panels, not only participant chips.

### Medium: Frontend Test Coverage Is Thin

Backend has broad pytest coverage. Frontend currently relies mainly on build checks and a small admin hook test. The play shell has little automated coverage for state transitions, stale participant cleanup, suggested action behavior, or error states.

Recommended first fix:

- Add focused React tests for `buildSceneParticipants`, action suggestions, turn consequence rendering, and admin token failure behavior.
- Keep visual screenshots for layout checkpoints, but do not use screenshots as the only regression signal.

## Gameplay And Immersion Findings

### Critical: Structural Anti-Stall Is Still Missing

The playtester report already proved prompt-only anti-stall rules were insufficient. The system needs a structural scene-progress governor: after repeated turns without a concrete change, the backend should force or strongly bias toward a new fact, cost, choice, clock movement, participant change, location change, or objective update.

Recommended first fix:

- Add a lightweight scene-progress summary derived from recent turns and consequences.
- Include explicit "last concrete changes" and "stalled turn count" in GM context.
- Add tests and rerun the 30-turn playtester benchmark.

### High: Mechanics Do Not Always Produce Player-Visible Moments

Dice rolls, inventory, conditions, clocks, secrets, scene art, and portraits exist, but the player feed only highlights some consequence types. Inventory and conditions can change without a strong in-feed moment. That weakens cause/effect.

Recommended first fix:

- Add player-safe consequence events for item deltas and condition applications/removals.
- Keep hidden mechanics hidden, but make visible consequences feel intentional.

### High: Suggested Actions Need Choice Design Rules

The provider must emit exactly three suggested actions, but there is no validation that they are distinct, objective-grounded, or non-repetitive. Poor suggestions can trap the player in the same loop the GM is trying to escape.

Recommended first fix:

- Validate suggested actions server-side for uniqueness and basic length.
- Include recent player action in the validator to reject direct restatements.
- Fall back to scene-aware local presets only when model suggestions are invalid.

### Medium: Sensory Systems Are Not Yet Joined To Gameplay State

Scene art is tied to location and portraits to character identity, but they do not yet react to stakes, conditions, faction pressure, or scene escalation. This is acceptable for early B-track work, but can feel static during tense scenes.

Recommended first fix:

- Add player-safe scene tags or tone metadata to scene art prompt/cache keys only when the location or high-level public scene state materially changes.
- Avoid regenerating art every turn.

## Documentation And Sprint State

- `CLAUDE.md` and `master-plan.md` present the project as ready for Wave 3 work.
- `master-plan.md` marks C2 finished, but `docs/development/workstreams/C2-operator-app.md` in the main checkout is still a template-like placeholder. The real C2 worktree has modified docs and missing screenshots. This should be reconciled before another agent resumes C2/C3.
- The parent roadmap still works as a high-level guide, but the immediate backlog needs a grooming checkpoint before A4/B4/C3 so feature slices do not pile onto unstable integration points.

## Recommended Grooming Order

1. **Security checkpoint:** enforce operator token backend-side and add tests.
2. **Provider contract repair:** wire live `condition_updates` and add provider tests.
3. **Scene anti-stall:** add backend scene-progress guardrails and rerun the playtester.
4. **Participant/state truth:** replace sessionStorage participant durability with server-derived scene presence.
5. **Admin campaign selection:** remove `test-campaign` default and make admin target selection explicit.
6. **UI honesty pass:** disable/label preview surfaces and improve visible consequence events.
7. **Docs reconciliation:** repair C2 workstream status and screenshot state.

## Suggested Branching

Use this review branch for documentation and grooming setup:

- `journey/2026-05-07-gameplay-ux-codebase-review`

Then split implementation into small branches:

- `groom/operator-token-gate`
- `groom/provider-condition-contract`
- `groom/scene-anti-stall`
- `groom/scene-presence-truth`
- `groom/admin-campaign-selection`

Each branch should update its workstream doc, run focused tests plus `make check`, and push before handoff.
