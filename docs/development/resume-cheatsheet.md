# Resume Cheatsheet

Use this file when a coding session is interrupted and you need another agent to continue without rebuilding context from scratch.

This wave of work is a **multi-track, multi-agent roadmap** (Codex / Claude / Gemini cycling through quotas). The handoff protocol is defined in `docs/development/agent-handoff-protocol.md` — read it once.

## Read Order (Every Agent, Every Session)

1. `CLAUDE.md` (or `AGENTS.md` for Codex, `GEMINI.md` for Gemini — they all point here)
2. `docs/development/agent-handoff-protocol.md`
3. `docs/development/master-plan.md` — the live "Now" dashboard
4. `docs/development/workstreams/{slice-id}-{title}.md` — the slice you are picking up
5. `cd` to the worktree path in the slice doc header
6. `git status` and `git log -5`

If `wip:` or `handoff:` is in the last commit message, read that diff before doing anything.

## Picking Up a Slice

If the slice is already in flight (branch + worktree + doc exist):
- `cd ~/ares-track-{x}/{ID}`
- read the workstream doc
- execute the **Next concrete step**, nothing else

If the slice is not yet started:
- from `~/ares` (the main checkout): `make bootstrap-slice SLICE=A1`
- this creates the branch, worktree, and workstream doc
- fill in Goal + Next concrete step in the new doc, then push

## Ending a Session

Before quota runs out / before stepping away:

1. Update the workstream doc — files touched, next concrete step, agent rotation log entry.
2. Commit:
   - `feat({ID}):` — done and tested
   - `wip({ID}):` — partial but tests green
   - `handoff({ID}):` — broken, doc explains state
3. Push the branch.

The next agent (possibly a different one) reads the doc + last commit and resumes.

## Copy-Paste Resume Prompts

Substitute `{slice-id}` (e.g. `A1`) and `{slice-doc}` (e.g. `A1-dice-skill-checks`) before pasting.

### For Codex

```text
Continue work in /home/lans/ares.

Read in this order:
1. AGENTS.md (or CLAUDE.md if AGENTS.md does not exist)
2. docs/development/agent-handoff-protocol.md
3. docs/development/master-plan.md
4. docs/development/workstreams/{slice-doc}.md

cd to the worktree path in the slice doc header. Run `git status` and `git log -5`.
If the last commit is `wip:` or `handoff:`, read its diff.

Resume from the literal "Next concrete step" in the slice doc.
Do not rediscover the task from scratch.

Before stopping, update the slice doc and make a feat:/wip:/handoff: commit.
If chat context and repo docs disagree, trust the repo docs.
```

### For Gemini

```text
Continue work in /home/lans/ares.

Read in this order:
1. GEMINI.md (or CLAUDE.md if GEMINI.md does not exist)
2. docs/development/agent-handoff-protocol.md
3. docs/development/master-plan.md
4. docs/development/workstreams/{slice-doc}.md

cd to the worktree path in the slice doc header. Run `git status` and `git log -5`.
If the last commit is `wip:` or `handoff:`, read its diff.

Resume from the literal "Next concrete step" in the slice doc.
Do not rediscover the task from scratch.

Before stopping, update the slice doc and make a feat:/wip:/handoff: commit.
If chat context and repo docs disagree, trust the repo docs.
```

### For Claude

```text
Continue work in /home/lans/ares.

Read in this order:
1. CLAUDE.md
2. docs/development/agent-handoff-protocol.md
3. docs/development/master-plan.md
4. docs/development/workstreams/{slice-doc}.md

cd to the worktree path in the slice doc header. Run `git status` and `git log -5`.
If the last commit is `wip:` or `handoff:`, read its diff.

Resume from the literal "Next concrete step" in the slice doc.
Do not rediscover the task from scratch.

Before stopping, update the slice doc and make a feat:/wip:/handoff: commit.
If chat context and repo docs disagree, trust the repo docs.
```

## Local Chat Artifact Paths (Supporting Context Only)

Use these only if the repo docs are insufficient. The repo docs are the source of truth.

- Codex sessions: `/home/lans/.codex/sessions/`
- Gemini sessions: `/home/lans/.gemini/tmp/ares/chats/`
- Claude task state: `/home/lans/.claude/tasks/`
- Claude plan files: `/home/lans/.claude/plans/`
  - Parent roadmap: `/home/lans/.claude/plans/a-i-happy-matsumoto.md`

## Rules

- Repo docs > chat artifacts. Always.
- Do not leave uncommitted edits across an agent handoff.
- Update the workstream doc **before** the handoff commit, not after.
- If the next step is unclear, the previous agent failed to update the doc — fix that before writing code.

## UI Work Resume Addendum

When resuming a UI slice, the workstream doc must contain a **"Last verified"** entry with:

- Before/after screenshot paths in `assets/samples/ui-iteration/`
- Checklist result (pass/fail per item)
- Known visual debt
- Exact next slice goal

If any of these are missing, take a baseline screenshot of the current state at `localhost:5180` before continuing, and record it as the new "before" checkpoint. Do not proceed without visual evidence of current state.

**Quick environment check on resume:**
```bash
curl -s http://localhost:5180/ | head -2 && echo OK || echo DOWN
# If DOWN: make compose-up
# Then seed intro bypass in browser: localStorage.ares_intro_seen=1
```
