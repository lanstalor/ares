# Agent Handoff Protocol

This wave of development (the fables.gg gap-closing roadmap) is run across **Codex, Claude, and Gemini**, cycling between agents as quotas exhaust. Sessions can be interrupted mid-edit. This document is the contract that keeps work resumable.

The parent roadmap is `~/.claude/plans/a-i-happy-matsumoto.md`. It defines three parallel tracks (A: Mechanical Depth, B: Sensory Polish, C: Operator Depth) and 15 slices total.

Read this once. The protocol is the only thing standing between "we picked up where we left off" and "we redid the same work three times."

---

## The Core Rule

**Every session ends with (1) a commit and (2) an updated workstream doc.** No exceptions. If the agent runs out of quota mid-thought, the next agent must be able to resume from `git log` + the workstream doc alone.

---

## Branch Model

One long-lived branch per slice, off `main`:

```
track-a/A1-dice-skill-checks
track-a/A2-itemized-inventory
track-a/A3-conditions
track-a/A4-combat-mode
track-a/A5-ability-registry
track-b/B1-media-provider
track-b/B2-scene-art
track-b/B3-portraits
track-b/B4-tts-narration
track-b/B5-world-map
track-c/C1-admin-api
track-c/C2-operator-app
track-c/C3-lore-pages
track-c/C4-session-prep
track-c/C5-continuity-review
```

- Open the branch the moment a slice starts (via `make bootstrap-slice SLICE=A1`).
- Branches stay open until the slice merges. Silence is fine; the workstream doc is the source of truth.
- `main` only receives merges of fully-verified slices. Half-done slices never touch `main`.

## Worktree Model

Up to three slices may be in flight at once (one per track). Use `git worktree` so checkouts do not collide:

```
~/ares                  → main
~/ares-track-a/A1       → track-a/A1-dice-skill-checks
~/ares-track-b/B1       → track-b/B1-media-provider
~/ares-track-c/C1       → track-c/C1-admin-api
```

`make bootstrap-slice` creates the branch, the worktree, the workstream doc, and the empty handoff commit in one shot.

---

## Workstream Doc Contract

Every active slice has a doc at `docs/development/workstreams/{slice-id}-{kebab-title}.md`. The template lives at `docs/development/workstreams/_template.md`.

The doc must always have these sections, accurate to the latest commit:

- **Header** — branch, worktree, PR, status, last agent, next agent
- **Goal** — one sentence
- **Last-known-good commit** — sha + test status at that sha
- **In-flight WIP** — clean | WIP commit sha + what works/breaks
- **Files touched so far** — running list
- **Next concrete step** — 1–3 sentences, literal next action
- **Open questions / blockers**
- **Agent rotation log** — append-only

This doc is the only thing a fresh agent must read to resume. Update it **before** the handoff commit at the end of every session.

---

## Commit Conventions

Three types of commits land on a slice branch:

| Prefix | Use |
|---|---|
| `feat(A1):` / `fix(A1):` | Working-state commit, tests green |
| `wip(A1):` | Tests green but slice not yet complete |
| `handoff(A1):` | Tests broken or mid-edit; doc explains state |

Every `handoff:` commit MUST be accompanied by a workstream-doc update describing what is broken and the literal next step.

Never leave uncommitted edits across an agent handoff. The next agent (a different process, possibly a different machine session) will not see your local diff.

---

## Resume Procedure (Every Agent, Every Session)

1. Read `CLAUDE.md` (Claude), `AGENTS.md` (Codex), or `GEMINI.md` (Gemini) — all three currently point to `CLAUDE.md`.
2. Read `docs/development/master-plan.md` — find which slices are in flight.
3. Read `docs/development/workstreams/{slice-id}.md` — the slice contract.
4. `cd` to the worktree path listed in the doc header.
5. Run `git status` and `git log -5`. Read the last commit's diff if it was a `wip:` or `handoff:`.
6. Execute the **Next concrete step**, nothing else.
7. Before stopping (or hitting quota), update the doc and create a commit (`feat:` / `wip:` / `handoff:`).

Per-agent copy-paste prompts live in `docs/development/resume-cheatsheet.md`.

---

## Slice Lifecycle

```
not-started ──► in-flight ──► review ──► merged
                    │
                    └──► blocked (only for real external blockers)
```

- **not-started** — branch + doc not yet created. Bootstrap with `make bootstrap-slice SLICE=A1` when you pick it up.
- **in-flight** — branch open, doc maintained, code being written.
- **review** — slice complete, draft PR marked ready, awaiting human merge.
- **merged** — branch deleted, worktree removed, doc moved to `docs/development/workstreams/_done/`.
- **blocked** — only for external dependencies (API key, asset delivery, schema decision pending). Not for "I don't know what to do next."

---

## The Master-Plan Dashboard

`docs/development/master-plan.md` "Now" table is the live dashboard. Whenever an agent picks up or drops a slice, it updates that row:

| Slice | Branch | Worktree | Agent | Status | Next step |
|---|---|---|---|---|---|

This is the first thing every agent reads after `CLAUDE.md`. One glance answers "what should I work on?" and "what is in flight?"

---

## Cross-Track Independence (Restated)

Track A, B, C never edit each other's owned files. Touch points are the typed seams:

- `Consequences` dataclass (Track A only extends)
- `NarrationProvider` / `MediaProvider` / `TTSProvider` Protocols (additive)
- Visibility enum (additive)
- Frontend component slots (each track owns specific components)

If two slices on different tracks want to touch the same file, the second one waits or coordinates explicitly via the workstream doc.

---

## Hard Constraints (from `CLAUDE.md`, restated for emphasis)

These apply to every slice on every track regardless of agent:

1. Hidden state never leaks to the player.
2. Canon guard is never bypassed (Darrow / Eo / Cassius / Virginia / Mustang are forbidden in narration).
3. Player character is Davan of Tharsis.
4. Campaign window is 728–732 PCE.
5. Provider abstraction is never bypassed — all AI calls go through a Protocol.
6. New external integrations gate behind a stub provider so dev/test work offline.

Any slice that violates these is rejected at PR review regardless of feature completeness.
