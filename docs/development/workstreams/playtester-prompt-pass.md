# Workstream: Playtester Prompt Pass

## Goal

Improve GM scene progression and reduce repetitive mid-scene stalls, then benchmark the result with the automated playtester using the repo's default provider path.

## Scope / Non-goals

- In scope: shared GM prompt changes, configurable playtester provider/model selection, playtester report metadata, and benchmark documentation.
- Out of scope: deeper turn-engine changes, new backend response fields, or UI changes to the live play shell.

## Current State

- The shared GM prompt now includes explicit anti-stall and anti-repetition rules.
- The playtester is no longer Claude-only. `tools/playtester/llm.py` now supports `openai` and `anthropic`, with role-specific overrides for player and evaluator.
- The default benchmark path follows the repo `.env`, which currently resolves to `openai:gpt-5.4-mini`.
- The playtester report now records the actual player/evaluator provider+model used.
- A short OpenAI smoke run succeeded and produced `tools/playtester/reports/2026-04-30-00-25.md`.
- A full 30-turn OpenAI benchmark succeeded and produced `tools/playtester/reports/2026-04-30-00-28.md`.

## Key Observations

- The harness improvements worked operationally: backend seeding, turn submission, scoring, and report generation all completed on the OpenAI path.
- Prompt-only changes did not solve the pacing problem. The full OpenAI benchmark still spent too many turns in static posture-management loops.
- Repetition remains the dominant failure mode. In the full 30-turn OpenAI report, `repetition` averaged `1.40`, with `flow` at `2.40` and `engagement` at `2.97`.
- The prompt changes helped define the desired contract, but they were not strong enough on their own to force real escalation every few turns.
- The provider change matters. The earlier Claude benchmark and the new OpenAI benchmark are directionally comparable, but not apples-to-apples. The harsher OpenAI evaluator path exposed how fragile the current scene-progression behavior still is.
- The next improvement slice should likely move beyond prompt-only rules and introduce stronger structural guardrails around escalation, scene churn, or repeated-beat suppression.

## Verification Run

- Verified on 2026-04-30:
  - `python3 -m compileall tools/playtester backend/app/services/anthropic_provider.py backend/app/services/openai_provider.py`
  - `backend/.venv/bin/pip install -r tools/playtester/requirements.txt`
  - `ARES_PLAYTESTER_TURNS=4 backend/.venv/bin/python tools/playtester/run.py`
  - `backend/.venv/bin/python tools/playtester/run.py`
- Runtime artifacts:
  - Smoke report: `tools/playtester/reports/2026-04-30-00-25.md`
  - Full benchmark: `tools/playtester/reports/2026-04-30-00-28.md`

## Next 1-3 Steps

1. Add a scene-level anti-stall safeguard that forces a new fact, cost, or choice after repeated turns in the same confrontation.
2. Consider evaluator-side benchmark normalization or provider pinning when comparing future runs against the original Claude baseline.
3. Re-run the full OpenAI playtester after the next structural anti-stall slice rather than relying on transcript spot checks alone.

## Session Update

- Date: 2026-04-30
- Agent: Codex
- Branch: `main`
- Commit / local state: dirty working tree with prompt/playtester changes and benchmark reports generated locally
- Status: implemented and benchmarked
- What changed: tightened the shared GM prompt around escalation and repetition, made the playtester provider/model configurable, defaulted the benchmark path to the repo provider settings, added report metadata, and ran OpenAI smoke/full benchmarks
- Verification run: compileall, playtester requirements install into `backend/.venv`, 4-turn OpenAI smoke, 30-turn OpenAI benchmark
- Known risks or unverified areas: the new prompt contract is still too soft to prevent long static loops; the new OpenAI benchmark is not directly equivalent to the earlier Claude benchmark
- Exact next step: build a structural anti-stall follow-up slice that forces scene progression beyond prompt wording alone
- GitHub links: not yet assigned
