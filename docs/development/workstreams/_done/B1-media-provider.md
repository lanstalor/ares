# Slice B1 — Media Provider

| Field | Value |
|---|---|
| **Track** | B |
| **Branch** | `track-b/B1-media-provider` |
| **Worktree** | `~/ares-track-b/B1` |
| **PR** | https://github.com/lanstalor/ares/pull/11 |
| **Status** | review |
| **Last agent** | Codex |
| **Next agent** | human review or B2 starter |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Add a provider-backed media abstraction for image generation that works offline by default and can later drive scene art and portrait generation.

## Last-known-good commit

`HEAD` — `feat(B1): add media provider abstraction`

Test status at this commit:
- backend (`make backend-test`): ✅ 77 passed
- frontend (`make check`): ✅ compileall + node syntax checks passed
- frontend (`npm run build`): ✅ passed after rebasing onto `origin/main` with PR #12 merged
- playtester (offline, stub provider): not-run (no turn-loop or frontend behavior changed)
- playwright screenshot at 5180: not-run (backend/provider-only slice)

## In-flight WIP

`clean` — provider abstraction and tests are complete; no known broken behavior.

## Files touched so far

- ✅ `backend/app/services/media_provider.py` — new `MediaProvider` Protocol, request/response dataclasses, stub provider, OpenAI image provider, Replicate image provider.
- ✅ `backend/app/services/provider_registry.py` — `get_media_provider()` selection via configured provider name/model.
- ✅ `backend/app/core/config.py` — `ARES_MEDIA_PROVIDER` and `ARES_MEDIA_MODEL` settings.
- ✅ `backend/app/api/routes/system.py` and `backend/app/schemas/system.py` — expose media provider readiness in `/api/v1/system/status`.
- ✅ `backend/tests/test_media_provider.py` — provider behavior with injected clients and offline stub coverage.
- ✅ `backend/tests/test_provider_registry.py` — registry coverage for stub, OpenAI, Replicate, and unknown media providers.

## Next concrete step

Open B2 on `track-b/B2-scene-art`: add the scene-art generation service/cache around `get_media_provider(settings.media_provider, settings.media_model)`, trigger it from location changes or an operator endpoint, and keep the default path stub-only/offline.

## Open questions / blockers

- Replicate is implemented with lazy import and injectable clients, but `replicate` is not yet a declared backend dependency. Add it in B2 only if the real Replicate path becomes an accepted runtime target.
- No media API route exists yet; that belongs in B2 with regenerate/list semantics.

## Agent rotation log

Append-only. One line per session.

- `2026-05-05 22:23 UTC` — Codex → implemented B1 media provider abstraction, config/status wiring, and tests; status review at `HEAD`.
- `2026-05-05 23:17 UTC` — Codex → rebased B1 onto updated `origin/main` after PR #12 scene-art baseline merge; verified `make backend-test` (77 passed), `make check`, and `npm run build`.

## Verification on completion

Before marking this slice **review**:

- [x] `make backend-test` passes
- [x] `make check` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [x] Workstream doc fully reflects final state
- [ ] Draft PR description summarizes the slice
- [ ] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Player character remains Davan of Tharsis
- [x] All AI/media/TTS calls go through a Provider Protocol
- [x] Stub provider works offline (no API key required for `make backend-test`)
