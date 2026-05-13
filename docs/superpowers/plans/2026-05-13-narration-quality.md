# Narration Quality — Plain Language & Tight Pacing — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut GM response length to 2–4 sentences for routine turns and eliminate invented sci-fi compound nouns from GM narration, by tightening the system prompt and surgically rewriting the world bible's Campaign Opening section.

**Architecture:** Two independent changes — (A) add a Length discipline section and replace the narrow TONE DOWN JARGON rule with a categorical Plain language section in `anthropic_provider.py`; (B) rewrite Section 14 of `world_bible.md` (GM Instructions block + Opening Message) to remove compound techno-nouns at the lore source. No schema migration, no UI changes.

**Tech Stack:** Python 3.12, pytest, world_bible.md (parsed by `world_bible_parser.py`)

---

## File Map

| File | Role |
|---|---|
| `backend/app/services/anthropic_provider.py` | Contains `_SYSTEM_PROMPT`. Add Length discipline section; replace TONE DOWN JARGON rule with Plain language section. |
| `world_bible.md` | Section 14 only: rewrite GM Instructions block + Opening Message to remove compound techno-nouns. |
| `backend/tests/test_anthropic_provider.py` | New tests asserting prompt structure. |
| `backend/tests/test_world_bible_parser.py` | New test asserting opening message is clean. |

---

## Task 1: Write failing tests for system prompt changes

**Files:**
- Modify: `backend/tests/test_anthropic_provider.py`

- [ ] **Step 1: Add import for `_SYSTEM_PROMPT`**

In `backend/tests/test_anthropic_provider.py`, add to the imports block (after the existing `from app.services.anthropic_provider import build_tool_schema` line):

```python
from app.services.anthropic_provider import _SYSTEM_PROMPT
```

- [ ] **Step 2: Add the four new test functions**

Append to the end of `backend/tests/test_anthropic_provider.py`:

```python
def test_system_prompt_has_length_discipline_section() -> None:
    assert "Length discipline:" in _SYSTEM_PROMPT


def test_system_prompt_has_plain_language_section() -> None:
    assert "Plain language (enforce every turn):" in _SYSTEM_PROMPT


def test_system_prompt_no_tone_down_jargon_rule() -> None:
    assert "TONE DOWN JARGON" not in _SYSTEM_PROMPT


def test_system_prompt_banned_terms_only_as_negative_examples() -> None:
    # Each banned term may appear at most once (as a "not X" example in the Plain language section).
    # They must not appear in positive-use framing anywhere else.
    banned = [
        "HoloCan",
        "BoQC sensor plate",
        "mag-rail service cradle",
        "wrist slate",
        "checkpoint blister",
    ]
    for term in banned:
        count = _SYSTEM_PROMPT.count(term)
        assert count <= 1, f"'{term}' appears {count} times in _SYSTEM_PROMPT — expected at most 1 (as negative example only)"
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_anthropic_provider.py::test_system_prompt_has_length_discipline_section tests/test_anthropic_provider.py::test_system_prompt_has_plain_language_section tests/test_anthropic_provider.py::test_system_prompt_no_tone_down_jargon_rule tests/test_anthropic_provider.py::test_system_prompt_banned_terms_only_as_negative_examples -v
```

Expected: 4 FAILED (sections not yet added; TONE DOWN JARGON still present)

---

## Task 2: Implement system prompt changes

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`

The `_SYSTEM_PROMPT` string starts at line 23 and ends at line 118. Two edits required.

- [ ] **Step 1: Insert the Length discipline section**

Locate the end of the "Pacing discipline" section and the start of "Scene change discipline:". The target line to insert after is:

```
- Treat stable scene facts as cached. Once the player knows where an object sits, how the room is lit, or how an NPC is standing, do not repeat it unless that fact changes or becomes tactically relevant.
- NPC physical tells are one-use per scene. If you used "jaw tightens," "eyes narrow," "hand stills," or any other body-language beat in a prior turn this session, do not repeat it. Vary the register entirely: cut to dialogue, cut to action, cut to consequence — do not reach for the same tell again.
- Avoid stacked atmospheric sentences that list sensory details without advancing the scene ("The station hums with X. Through the viewport, Y hangs Z. The air smells of W."). Each sentence must earn its place by moving something — action, tension, character, or information. Cut anything that just paints the furniture.
```

After that block and before `Scene change discipline:`, insert:

```
Length discipline:
- Routine turns: target 2–4 sentences, ~80–150 words. A routine turn is any player action that does not resolve a major arc event.
- Major beats: combat resolution, secret reveal, location change, objective completion — up to 6 sentences, ~200–250 words. These are the exceptions, not the baseline.
- Audit rule: if you are past 4 sentences on a routine turn, cut the weakest sentence before finalizing.
- Before/after: BAD — five sentences establishing atmosphere plus two sentences of consequence. GOOD — one sentence naming what changed, two sentences of consequence and sensory grounding, done.

```

- [ ] **Step 2: Replace the TONE DOWN JARGON rule with the Plain language section**

In the `Prose discipline — what to cut:` section, replace this exact bullet:

```
- TONE DOWN JARGON: Do not overwhelm the player with dense mechanical or spatial jargon (e.g., "seam", "rip", "lane", "buffer fault 19-B", "lacquered strip"). Use plain, accessible descriptions for the environment and actions. You are writing a gritty political thriller, not a technical manual for spaceship repair. Keep the focus on the tension and the stakes, not the mechanics of the objects.
```

With this new block (note: this replaces only that one bullet; the rest of Prose discipline remains):

```
Plain language (enforce every turn):
- Ban invented compound techno-nouns: any invented term formed as [Acronym]-[noun] (BoQC, HoloCan), [Material]-[noun]-[noun] (mag-rail service cradle), or a capitalized technical brand for a mundane object (checkpoint blister, wrist slate, private-band buffer). Describe what the thing does or means to the character, not its designation.
- Allowed flavor: canon Red Rising terms — Color names (Gold, Red, Gray, Obsidian, Blue, Copper, Silver), weapons (scorcher, razor, pulseFist, gravBoots), Society hierarchy (Peerless Scarred, Praetor, Legate), Sons of Ares, the Weaver, ghost packet, dead-channel ping.
- NPC titles on non-formal mention: use short form after introduction. "Legate Voss ti Harlan" on first appearance; "Voss" or "the Legate" thereafter. "Station Chief Pelsin si Vorath" on introduction; "Pelsin" thereafter.
- Plain substitutions to use: "comms repeater" (not HoloCan repeater), "surveillance plate" (not BoQC sensor plate), "maintenance cradle" (not mag-rail service cradle), "checkpoint" (not checkpoint blister), "wrist panel" (not wrist slate), "rad badge" (not dose counters), "shift timer" (not shift clock).
```

- [ ] **Step 3: Run the four prompt tests to confirm they pass**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_anthropic_provider.py::test_system_prompt_has_length_discipline_section tests/test_anthropic_provider.py::test_system_prompt_has_plain_language_section tests/test_anthropic_provider.py::test_system_prompt_no_tone_down_jargon_rule tests/test_anthropic_provider.py::test_system_prompt_banned_terms_only_as_negative_examples -v
```

Expected: 4 PASSED

- [ ] **Step 4: Run the full existing prompt test to confirm no regression**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_anthropic_provider.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd /home/lans/ares && git add backend/app/services/anthropic_provider.py backend/tests/test_anthropic_provider.py && git commit -m "feat: add length discipline and plain language rules to GM system prompt"
```

---

## Task 3: Write failing test for world bible opening message

**Files:**
- Modify: `backend/tests/test_world_bible_parser.py`

- [ ] **Step 1: Add the new test**

Append to the end of `backend/tests/test_world_bible_parser.py`:

```python
def test_opening_message_contains_no_compound_techno_nouns() -> None:
    """Opening message must not seed the GM with compound techno-nouns."""
    raw = _load_world_bible()
    # Extract the Opening Message block between the heading and its closing fence
    start_marker = "### Opening Message (Player-facing)\n\n```"
    end_marker = "```"
    start_idx = raw.index(start_marker) + len(start_marker)
    end_idx = raw.index(end_marker, start_idx)
    opening_message = raw[start_idx:end_idx]

    banned = [
        "HoloCan",
        "BoQC sensor plate",
        "mag-rail service cradle",
        "wrist slate",
        "checkpoint blister",
        "dose counters",
    ]
    for term in banned:
        assert term not in opening_message, (
            f"Banned compound techno-noun '{term}' found in opening message"
        )
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_world_bible_parser.py::test_opening_message_contains_no_compound_techno_nouns -v
```

Expected: FAILED — multiple banned terms found in opening message

---

## Task 4: Rewrite world_bible.md Section 14

**Files:**
- Modify: `world_bible.md` (Section 14 only, lines ~1242–1336)

Two sub-edits: (A) GM Instructions block, (B) Opening Message.

### 4A — GM Instructions block

Note: `mag-rail service cradle` only appears in the GM Instructions block (not the Opening Message, which already says "maintenance cradle").

- [ ] **Step 1: Replace `mag-rail service cradle` in the GM Instructions block**

Find (in the GM Instructions code fence, around line 1268):
```
outside the pressure rim in a mag-rail service cradle with
```
Replace with:
```
outside the pressure rim in a maintenance cradle with
```

- [ ] **Step 2: Replace `checkpoint blister` in the GM Instructions block**

Find (around line 1269):
```
from the checkpoint blister. Station Chief Pelsin si Vorath's
```
Replace with:
```
from the checkpoint. Station Chief Pelsin si Vorath's
```

- [ ] **Step 3: Replace `dose counters, shift clocks` in the GM Instructions block**

Find (around line 1273):
```
oppression is procedural: dose counters, shift clocks,
```
Replace with:
```
oppression is procedural: rad badges, shift timers,
```

- [ ] **Step 4: Replace the "player-facing terms are concrete" block**

Find (lines 1277–1285):
```
The player-facing terms are concrete:
- The Weaver is Mara's anonymous Sons handler, not a public title
  or known identity. They send orders through dead relay pings and
  never meet Mara in person.
- Relay 19 is an exterior communications mast on Ganymede's pressure
  rim: HoloCan repeater, BoQC sensor plate, emergency beacon, and
  private Gold band stacked into one tower.
- The ghost packet is a corrupted data fragment stuck in Relay 19's
  buffer. Mara does not know what it means yet.
```
Replace with:
```
Use plain, grounded language in narration. Keep the focus on tension
and stakes, not the names of hardware:
- The Weaver is Mara's anonymous Sons handler. They send orders through
  dead relay pings and never meet Mara in person.
- Relay 19 is the exterior comms mast above Mara: a comms repeater,
  surveillance plate, emergency beacon, and private Gold band stacked
  into one tower.
- The ghost packet is a corrupted data fragment stuck in Relay 19's
  buffer. Mara does not know what it means yet.
```

### 4B — Opening Message

- [ ] **Step 5: Replace `shift clock` in the Opening Message**

Find (around line 1305):
```
eighteen minutes of exterior clearance before the shift clock
starts billing your body as waste.
```
Replace with:
```
eighteen minutes of exterior clearance before the shift timer
starts billing your body as waste.
```

- [ ] **Step 6: Replace `checkpoint blister` in the Opening Message**

Find (around line 1312):
```
Two Gray supervisors watch from the checkpoint blister inside
```
Replace with:
```
Two Gray supervisors watch from the checkpoint inside
```

- [ ] **Step 7: Replace the relay mast diagnostic listing in the Opening Message**

Find (around line 1316):
```
The relay mast above you ticks through its diagnostic warm-up:
carrier light, HoloCan repeater, BoQC sensor plate, private
Gold band. In twenty minutes Station Chief Pelsin si Vorath's
morning scrub will overwrite the buffer.
```
Replace with:
```
The relay mast above you ticks through its diagnostic warm-up:
carrier light, comms repeater, surveillance plate, private
Gold band. In twenty minutes Station Chief Pelsin si Vorath's
morning scrub will overwrite the buffer.
```

- [ ] **Step 8: Replace the exposition paragraph in the Opening Message**

Find (around line 1320):
```
The Weaver is your anonymous Sons handler, a voice in dead relay
pings and borrowed maintenance codes. Relay 19 is the exterior mast
above you: HoloCan repeater, Board of Quality Control sensor plate,
emergency beacon, private Gold band. The ghost packet is a corrupted
data fragment stuck in its buffer. You do not know what it means yet.
```
Replace with:
```
The Weaver is your anonymous Sons handler, a voice in dead relay
pings and borrowed maintenance codes. Relay 19 is the exterior mast
above you. The ghost packet is a corrupted data fragment stuck in its
buffer. You do not know what it means yet.
```

### 4C — Run and verify

- [ ] **Step 9: Run the new world bible test**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_world_bible_parser.py::test_opening_message_contains_no_compound_techno_nouns -v
```

Expected: PASSED

- [ ] **Step 10: Run the full world bible test suite to confirm no regressions**

```bash
cd /home/lans/ares && docker compose exec backend pytest tests/test_world_bible_parser.py -v
```

Expected: all PASSED. The existing assertion `"Surface Relay Tower 19" in seed.campaign_opening.opening_message` must still pass — the tower name is untouched. The clock label `"BoQC Heat"` comes from the Clocks table (untouched), not the Opening Message, so it still passes.

- [ ] **Step 11: Commit**

```bash
cd /home/lans/ares && git add world_bible.md backend/tests/test_world_bible_parser.py && git commit -m "feat: rewrite world bible Section 14 — plain language opening message and GM instructions"
```

---

## Task 5: Full test suite pass

**Files:** none

- [ ] **Step 1: Run all backend tests**

```bash
cd /home/lans/ares && docker compose exec backend pytest --tb=short -q
```

Expected: all tests pass (237+ passing, 0 failures). If failures appear, fix them before proceeding.

---

## Task 6: Rebuild backend and run playtest

- [ ] **Step 1: Rebuild backend container with new code**

```bash
cd /home/lans/ares && docker compose up --build --no-deps -d backend
```

Wait for the container to report healthy:
```bash
docker compose ps backend
```
Expected: `Up` or `healthy`.

- [ ] **Step 2: Run the 20-turn playtest**

```bash
cd /home/lans/ares && python tools/playtester/run_playtest.py --turns 20
```

The script saves a report to `tools/playtester/reports/`. Note the filename it outputs.

- [ ] **Step 3: Verify success thresholds**

Open the report file at `tools/playtester/reports/<timestamp>.md` and manually check:

1. **Median GM response length ≤ 800 chars** — count all `GM (chars: N)` lines; majority should be ≤ 800.
2. **Turn 1 GM response ≤ 1000 chars** — first GM response.
3. **Zero banned terms in any GM turn** — grep for `HoloCan`, `BoQC sensor plate`, `mag-rail service cradle`, `wrist slate`, `checkpoint blister`:
   ```bash
   grep -i "HoloCan\|BoQC sensor\|mag-rail service\|wrist slate\|checkpoint blister" tools/playtester/reports/<timestamp>.md
   ```
   Expected: no output.
4. **Evaluator Engagement/Flow ≥ 4.0** — check per-turn scores.

If any threshold is missed, diagnose and iterate before moving to Task 7. Common fixes:
- If banned terms still appear: check the world bible rewrite landed correctly and backend was rebuilt.
- If responses are still too long: tighten the Length discipline wording (add a worked example showing a bad 6-sentence response cut to 3).

- [ ] **Step 4: Commit the playtest report**

```bash
cd /home/lans/ares && git add tools/playtester/reports/ && git commit -m "test: narration quality 20-turn playtest report"
```

---

## Task 7: Open PR

- [ ] **Step 1: Push branch to origin**

```bash
cd /home/lans/ares && git push -u origin HEAD
```

- [ ] **Step 2: Create the PR**

```bash
gh pr create --title "feat: narration quality — plain language and tight pacing (Wave 3)" --body "$(cat <<'EOF'
## Summary
- Adds **Length discipline** section to GM system prompt: 2–4 sentences / 80–150 words for routine turns; major beats up to 6 sentences
- Replaces narrow TONE DOWN JARGON rule with categorical **Plain language** section naming banned compound techno-nouns (`HoloCan`, `BoQC`, `mag-rail service cradle`, etc.) and a canon whitelist
- Rewrites world_bible.md Section 14 (GM Instructions + Opening Message) to remove compound techno-nouns at the lore source — the opening seeds the GM's register each session, so this is the root fix

## Test plan
- [ ] 4 new unit tests for system prompt structure (`Length discipline` present, `Plain language` present, `TONE DOWN JARGON` absent, banned terms ≤ 1 occurrence each)
- [ ] 1 new unit test asserting opening message contains no banned compound techno-nouns
- [ ] Full 237+ test suite passing
- [ ] 20-turn Haiku playtest: median GM ≤ 800 chars, Turn 1 ≤ 1000 chars, zero banned terms, Engagement/Flow ≥ 4.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
