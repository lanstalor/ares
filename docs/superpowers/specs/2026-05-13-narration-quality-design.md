# Narration Quality — Plain Language & Tight Pacing — Design Specification

**Date:** 2026-05-13
**Track:** Wave 3 (post A4 combat)
**Goal:** Cut GM response length to 80–150 words for routine turns and eliminate invented sci-fi compound nouns from GM narration.

---

## Problem Statement

GM responses in the 2026-05-12 playtest grow from **1248 chars (Turn 1) to 2503 chars (Turn 11)** — roughly 200 words rising to 500+ — with no plateau. The opening turn already contains: `mag-rail service cradle`, `HoloCan repeater`, `BoQC sensor plate`, `private-band buffer instability`, `checkpoint blister`, `wrist slate`, `shift clock`, `dose counters`, `scorcher`.

Root causes:

1. **World bible seeds the jargon register.** Section 14's GM Instructions block tells the AI that terms like `HoloCan`, `BoQC`, `mag-rail service cradle`, and `checkpoint blister` are "concrete and player-facing." The Opening Message (shown to the player on Turn 1 and immediately present in `recent_turns` history) uses these terms verbatim. The GM mirrors the register it sees in its context.

2. **System prompt jargon rule is too narrow.** The existing "TONE DOWN JARGON" rule in Prose discipline only bans specific artifacts from earlier playtests (`seam`, `rip`, `lane`, `buffer fault 19-B`, `lacquered strip`). It does not name the categories of jargon or the terms flooding in from the seed.

3. **No length cap.** The existing Pacing discipline says "calibrate length to the action" — vague enough for the GM to ignore. No target word count is stated. The GM defaults to atmospheric expansion.

---

## Solution

Two coordinated changes, no schema migration, no UI changes.

---

## Change A — World Bible Surgical Rewrite

**File:** `world_bible.md` — Section 14 only (~95 lines)

Rewrite the GM Instructions block and the player-facing Opening Message to use plain, grounded language. The rest of the world bible's rich lore (locations, NPCs, factions, history) is untouched — the GM reads it as hidden context but does not mirror it into narration the same way it mirrors the opening message.

### Term substitution table

| Original | Replacement |
|---|---|
| `mag-rail service cradle` | `maintenance cradle` |
| `HoloCan repeater` | `comms repeater` |
| `BoQC sensor plate` | `surveillance plate` |
| `private-band buffer instability` | `private-channel instability` |
| `checkpoint blister` | `checkpoint` |
| `wrist slate` | `wrist panel` |
| `shift clock` | `shift timer` |
| `dose counters` | `rad badge` |
| `dead-channel ping` | `dead-channel ping` (keep — evocative, not compound techno-noun) |
| `ghost packet` | `ghost packet` (keep — is a plot MacGuffin; player must learn it) |
| `Pelsin si Vorath` | keep — canon NPC name |
| `scorcher` | keep — canon weapon term |

### GM Instructions block rewrites

Remove: `"The player-facing terms are concrete: - Relay 19 is an exterior communications mast on Ganymede's pressure rim: HoloCan repeater, BoQC sensor plate, emergency beacon, and private Gold band stacked into one tower."`

Replace with: `"Use plain, grounded language in narration. Keep the focus on tension and stakes, not the names of hardware. The comms repeater, surveillance plate, and emergency beacon are components of the relay mast — describe what they do or what they mean to Mara, not their technical designations."`

### Opening Message rewrite

Rewrite the Opening Message to remove compound techno-nouns while preserving the scene setup, stakes, and Red Rising flavor. The rewrite keeps: Color names, `ghost packet`, `dead-channel ping`, `Oran of Cimmeria`, `Pelsin si Vorath`, `the Weaver`, `Sons`, `razor`/`scorcher` (if used), `rad badge` (replacing `dose counters`).

---

## Change B — System Prompt Tightening

**File:** `backend/app/services/anthropic_provider.py` — `_SYSTEM_PROMPT`

### B1 — New "Length discipline" section

Add a new named section immediately after "Pacing discipline":

```
Length discipline:
- Routine turns: target 2–4 sentences, ~80–150 words. A routine turn is any player action that does not resolve a major arc event.
- Major beats: combat resolution, secret reveal, location change, objective completion — up to 6 sentences, ~200–250 words. These are the exceptions, not the baseline.
- Audit rule: if you are past 4 sentences on a routine turn, cut the weakest sentence before finalizing.
- Before/after: BAD — five sentences establishing atmosphere plus two sentences of consequence. GOOD — one sentence naming what changed, two sentences of consequence and sensory grounding, done.
```

### B2 — Replace and expand "TONE DOWN JARGON" rule

Replace the existing single-bullet TONE DOWN JARGON rule with a new categorical "Plain language" section:

```
Plain language (enforce every turn):
- Ban invented compound techno-nouns: any invented term formed as [Acronym]-[noun] (BoQC, HoloCan), [Material]-[noun]-[noun] (mag-rail service cradle), or a capitalized technical brand for mundane hardware (checkpoint blister, wrist slate, shift clock, private-band buffer). Describe what the thing does, not its designation.
- Allowed flavor: canon Red Rising terms — Color names (Gold, Red, Gray, Obsidian, Blue, Copper, Silver), weapons (scorcher, razor, pulseFist, gravBoots), the Society's hierarchy terms (Peerless Scarred, Praetor, Legate), Sons of Ares, the Weaver, ghost packet, dead-channel ping.
- NPC titles on first non-formal mention: use short form. "Legate Voss ti Harlan" on introduction; "Voss" or "the Legate" thereafter. Station Chief Pelsin is "Pelsin" after first introduction.
- Plain substitutions: "comms repeater" (not HoloCan repeater), "surveillance plate" (not BoQC sensor plate), "maintenance cradle" (not mag-rail service cradle), "checkpoint" (not checkpoint blister), "wrist panel" (not wrist slate), "rad badge" (not dose counters).
```

---

## Files Touched

| File | Change |
|---|---|
| `world_bible.md` | Section 14 rewrite: GM Instructions block + Opening Message |
| `backend/app/services/anthropic_provider.py` | New Length discipline section; replace TONE DOWN JARGON with Plain language section |
| `backend/tests/test_anthropic_provider.py` | New tests (see below) |
| `docs/superpowers/specs/2026-05-13-narration-quality-design.md` | This file |
| `docs/superpowers/plans/2026-05-13-narration-quality.md` | Implementation plan |

---

## Test Strategy

### Unit tests (backend/tests/test_anthropic_provider.py)

1. **Length discipline section present:** `"Length discipline" in _SYSTEM_PROMPT`
2. **Plain language section present:** `"Plain language" in _SYSTEM_PROMPT`
3. **Old TONE DOWN JARGON rule replaced:** `"TONE DOWN JARGON" not in _SYSTEM_PROMPT`
4. **Banned terms appear only as negative examples:** `HoloCan`, `BoQC`, `mag-rail service cradle`, `wrist slate`, `checkpoint blister` each appear in `_SYSTEM_PROMPT` at most once — inside the Plain language substitution list as `(not X)` examples. Assert count ≤ 1 for each. They must not appear in positive-use framing anywhere else in the prompt.
5. **World bible parser loads rewritten Section 14 without error** (existing parser tests cover this implicitly; no new parser test needed unless the parser is regex-sensitive to the rewrite).
6. **Opening message does not contain banned terms:** Load `world_bible.md`, extract the Opening Message block (between `### Opening Message (Player-facing)` and the closing fence), assert none of `HoloCan`, `BoQC`, `mag-rail service cradle`, `wrist slate`, `checkpoint blister`, `dose counters` appear.

### Playtest (20 turns, Haiku player + Haiku evaluator)

Success thresholds:
- **Median GM response length ≤ 800 chars** (current ~1500–2000)
- **Turn 1 GM response ≤ 1000 chars** (current 1248)
- **Zero occurrences** of `HoloCan`, `BoQC`, `mag-rail service cradle`, `wrist slate`, `checkpoint blister` in any GM turn
- **Evaluator Engagement/Flow ≥ 4.0** (do not regress vs. current 4.5 — allow 0.5 tolerance for Haiku variance)

---

## Risks

| Risk | Mitigation |
|---|---|
| Stripping flavor makes the setting feel generic | Canon whitelist preserves Red Rising vocabulary; `ghost packet`, `the Weaver`, `dead-channel ping` keep the unique texture |
| Existing campaigns have old opening text in turn history | Acceptable — single-player game, campaigns are reseeded for testing; fix is forward-looking |
| Haiku evaluator scores everything 5.0 (seen before) | Also assert raw char counts from the playtest report, not just evaluator scores |
| GM creep: prompt tightens but GM slowly re-expands over 20 turns | Audit rule ("if past 4 sentences, cut") is self-referential and visible every turn; playtest run is 20 turns to catch drift |
