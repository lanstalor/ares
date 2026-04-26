# Resume Cheatsheet

Use this file when a coding session is interrupted and you need another agent to continue without rebuilding context from scratch.

## Read Order

Always point the next agent at these repo files first:

1. `CLAUDE.md`
2. `docs/development/master-plan.md`
3. The active workstream doc linked under `Now`
4. `git status`

Only use raw chat artifacts as supporting context after those four sources.

## Current Active Slice

- Issue: `#5`
- Branch: `feat-5-gm-scene-context`
- Draft PR: `#6`
- Workstream doc: `docs/development/workstreams/gm-scene-context-and-guidance.md`

## Latest Local Chat Artifacts

These are machine-local paths on this VM, not repo files.

- Codex:
  `/home/lans/.codex/sessions/2026/04/26/rollout-2026-04-26T13-43-35-019dca07-fe8a-71e1-9028-2d37c9419893.jsonl`
- Gemini:
  `/home/lans/.gemini/tmp/ares/chats/session-2026-04-25T21-39-3628096c.jsonl`
- Gemini lightweight session:
  `/home/lans/.gemini/tmp/ares/chats/session-2026-04-26T09-31-dfc9c8c9.jsonl`

Claude local task state exists under `/home/lans/.claude/tasks/`, but it is less reliable as a clean resume source than the repo docs plus the Codex/Gemini JSONL files.

## Copy-Paste Prompts

### For Codex

```text
Continue work in /home/lans/ares.

Read in this order:
1. CLAUDE.md
2. docs/development/master-plan.md
3. docs/development/workstreams/gm-scene-context-and-guidance.md
4. git status

Use this raw chat artifact only if needed for supporting context:
/home/lans/.codex/sessions/2026/04/26/rollout-2026-04-26T13-43-35-019dca07-fe8a-71e1-9028-2d37c9419893.jsonl

Resume from the exact next step in the workstream doc.
Do not rediscover the task from scratch.
If chat context and repo docs disagree, trust the repo docs until revalidated.
```

### For Gemini

```text
Continue work in /home/lans/ares.

Read in this order:
1. CLAUDE.md
2. docs/development/master-plan.md
3. docs/development/workstreams/gm-scene-context-and-guidance.md
4. git status

Use these local chat artifacts only if needed for supporting context:
- /home/lans/.codex/sessions/2026/04/26/rollout-2026-04-26T13-43-35-019dca07-fe8a-71e1-9028-2d37c9419893.jsonl
- /home/lans/.gemini/tmp/ares/chats/session-2026-04-25T21-39-3628096c.jsonl

Resume from the exact next step in the workstream doc.
Do not rediscover the task from scratch.
If chat context and repo docs disagree, trust the repo docs until revalidated.
```

### For Claude

```text
Continue work in /home/lans/ares.

Read in this order:
1. CLAUDE.md
2. docs/development/master-plan.md
3. docs/development/workstreams/gm-scene-context-and-guidance.md
4. git status

Use this Codex chat artifact only if needed for supporting context:
/home/lans/.codex/sessions/2026/04/26/rollout-2026-04-26T13-43-35-019dca07-fe8a-71e1-9028-2d37c9419893.jsonl

Resume from the exact next step in the workstream doc.
Do not rediscover the task from scratch.
If chat context and repo docs disagree, trust the repo docs until revalidated.
```

## Rules

- Do not treat the raw chat artifact as the source of truth when a workstream doc exists.
- Update the workstream doc before pausing if the next step changed.
- If the branch is dirty, make sure the workstream doc mentions the local state before switching agents.
