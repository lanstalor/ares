# Gemini Agent Bootstrap

Gemini sessions: read `CLAUDE.md` first — it is the canonical project bootstrap for all agents on this repo.

Then read:

1. `docs/development/agent-handoff-protocol.md` — multi-agent handoff rules (Codex / Claude / Gemini share branches and slice docs).
2. `docs/development/master-plan.md` — the live "Now" dashboard of in-flight slices.
3. The slice doc under `docs/development/workstreams/` corresponding to the work you are picking up.

Resume prompts and conventions live in `docs/development/resume-cheatsheet.md`.

The parent roadmap for the current wave (fables.gg gap-closing) is at `~/.claude/plans/a-i-happy-matsumoto.md`.

**Before stopping, always:**
1. Update the slice doc.
2. Commit (`feat(ID):` / `wip(ID):` / `handoff(ID):`).
3. Push.
