# Codex Handoff: Full UI Overhaul

**Status of prior work:** A CSS layer was added (`UI OVERHAUL — PIXEL TERMINAL` at the bottom of `styles.css`) that added VT323 font, some CSS frame primitives, and a red EXECUTE button. **The layout wireframe was NOT changed. The information architecture was NOT changed. The reference image was NOT implemented.** This document is the authoritative spec for the actual work that needs doing.

**Reference image:** `assets/samples/ui.png` — study it before reading anything else.  
**Style guide:** `docs/layout.md` — read fully, pay special attention to §"What to Change" and §"Style Guide".  
**Dev workflow:** `docker compose up --build --no-deps -d frontend` to rebuild after changes; verify the direct game shell at `http://localhost:5180/` with Playwright screenshot. For direct-to-game captures, seed browser localStorage with `ares_intro_seen=1`; do not use `/ui-dev` for UI-overhaul testing.

---

## What the Reference Image Actually Shows

Analyzing `assets/samples/ui.png` at the pixel level:

### Overall Layout (3-column + bottom bar)

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOPBAR: ARES brand | location breadcrumb | tactical stats (tiny)   │
├──────────────┬──────────────────────────────────┬───────────────────┤
│  NARRATIVE   │                                  │  RIGHT UTILITY    │
│  FEED        │      SCENE VIEWPORT              │  PANELS (stacked) │
│  (narrow,    │      (large, dominant,            │                   │
│  ~22% width) │      ~55% width)                 │  • OUTPOST RADAR  │
│              │                                  │  • SIGNAL/TELEM   │
│  Log-style   │  - thick monitor bezel           │  • STATUS bars    │
│  panels with │  - scene image darkened          │                   │
│  heavy frame │  - title overlay (top-left)      │  (~23% width)     │
│  borders     │  - objective inset (bottom)      │                   │
│              │                                  │                   │
├──────────────┴──────────────────────────────────┴───────────────────┤
│  SCENE PRESENCE STRIP (spans all 3 columns, portrait cards w/ HP)   │
├─────────────────────────────────────────────────────────────────────┤
│  COMMAND BAR: [TALK] [BRIBE] [SNEAK] [INSPECT]  textarea  [EXECUTE] │
└─────────────────────────────────────────────────────────────────────┘
```

### Key structural differences from current code

| Region | Current code | Reference image |
|---|---|---|
| Layout columns | 2 columns: play-column + 56px icon rail | 3 columns: feed (~22%) + scene (~55%) + utility (~23%) |
| Right panel | Icon rail (56px) + collapsing popout | Always-visible stacked utility panels |
| Action buttons | Hidden in a popover triggered by a lightbulb icon | Prominent hardware-style row: TALK / BRIBE / SNEAK / INSPECT visible at all times in the command bar |
| Narrative feed | ~40% width, takes up left half of layout | ~22% width, narrow log column |
| Scene viewport | ~60% width, center of layout | ~55% width, visually dominant with thick bezel |
| Presence strip | Compact row below scene only | Full-width row spanning all 3 columns, portrait cards |
| Command line | Combined with action bar inside play-column | Separate full-width bottom bar with visible action tabs |
| Panel depth | 1px border + top accent strip | THICK borders (3-4px), inset surfaces, visible bevel, hard enclosure |
| Turn cards | Styled message blocks | Heavy framed log entries with left source badge |

---

## Structural Changes Required

### 1. Restructure `App.jsx` layout

**Current structure:**
```
.app-shell
  .topbar
  .layout
    .play-column
      .story-grid
        TurnFeed          ← ~40% of story-grid
        .scene-column
          SceneBackdrop
          ParticipantStrip
      PlayerInput         ← contains ActionBar + textarea + submit
  StatusPanel             ← collapsing icon-rail popout (56px)
```

**Target structure:**
```
.app-shell
  .topbar                 ← thinner, darker, all VT323 pixel font
  .main-grid              ← 3-column grid
    .feed-column          ← ~22% width, always-visible narrative log
      TurnFeed
    .scene-column         ← ~55% width, monitor viewport
      SceneBackdrop
    .utility-column       ← ~23% width, always-visible stacked panels
      UtilityPanels (character stats, signal telemetry, map placeholder)
  .presence-bar           ← full-width row: ParticipantStrip
  .command-bar            ← full-width bottom: action tabs + textarea + execute
    ActionTabStrip        ← TALK / BRIBE / SNEAK / INSPECT always visible
    textarea
    button.execute
```

The `StatusPanel` (icon rail + popout) is REPLACED by an always-visible `.utility-column`.

### 2. Rewrite `PlayerInput.jsx` and `ActionBar.jsx`

The current ActionBar is a lightbulb popover. Replace with a static tab row.

**Target command bar layout:**
```
[ares>] [__________ textarea ___________] | [TALK] [BRIBE] [SNEAK] [INSPECT] | [EXECUTE]
```
Or with the action tabs above:
```
[TALK] [BRIBE] [SNEAK] [INSPECT]
[ares>] [__________ textarea ___________]                              [EXECUTE]
```

The reference shows 4 visible action buttons with numbers (1-4) in the bottom bar, always visible. Clicking one fills the textarea. EXECUTE is on the far right.

### 3. Utility column replaces icon sidebar

The StatusPanel icon rail + popout collapses. Instead, the right column is always visible with stacked panels:

- **Character/Operative** — name, caste, HP bar, level
- **Signal Telemetry** — health status bars, connection strength (like the SIGNAL TELEMETRY panel in the reference with bar graphs)
- **Outpost Radar / Map** — currently a placeholder box is fine (reference shows a minimap area with a grid)
- **Active Objective** — current mission objective

These are the same StatusPanel sub-panels refactored as always-visible stacked modules in a column.

### 4. ParticipantStrip moves to full-width row

Currently inside `.scene-column`. Move outside the 3-column grid, spanning all columns between the main grid and the command bar. This makes presence cards larger and more prominent per the reference.

---

## Visual Language — What Every Panel Must Look Like

The reference uses a consistent panel grammar that we have NOT implemented. Every panel needs:

```
┌──┬─────────────────────────────────────┬──┐  ← thick outer border (2-3px, dark teal)
│  │ ▌PANEL TITLE                 [chip] │  │  ← title strip with left accent bar
│  ├─────────────────────────────────────┤  │  ← divider line
│  │                                     │  │  
│  │  content area                       │  │  ← darker inset surface
│  │  (lower-brightness inner bg)        │  │
│  │                                     │  │
└──┴─────────────────────────────────────┴──┘
    ↑ corner bracket markers (2px lines)
```

Key visual properties that must be real, not implied:
- **Outer border: 2px solid** with high-opacity steel/teal (not rgba 0.22 — it must be VISIBLE)
- **Inner inset: box-shadow inset** — the panel content area should look sunken
- **Title strip height: ~24px** with background slightly lighter than panel, and a **colored left edge bar** (4px wide, full height of title strip, using `--panel-accent`)
- **Corner bracket markers**: actual `::before`/`::after` pseudo-elements drawing L-shaped brackets (not just opacity overlays)
- **Background of content area**: noticeably darker than the outer border — creates the "inset screen" effect

### Turn Feed (narrative log)

Each turn entry in the reference looks like:
```
┌─────────────────────────────────────────┐
│ [DA] DAVAN O'THARSIS    4/30, 12:25     │  ← source badge + name + timestamp
├─────────────────────────────────────────┤
│ The player's action text here...        │  ← body, full opacity
└─────────────────────────────────────────┘
```
With a **left-side colored stripe** (red for player, amber for GM, cyan for system). The border on each card must be clearly visible. The "current moment" card at top is larger with a portrait avatar.

### Presence Strip (participant cards)

Reference shows portrait-style cards:
```
┌──────────────────────────────┐
│  [portrait] Name             │
│  Role / Affiliation          │
│  ██████░░░░ HP  ● FRIENDLY   │
└──────────────────────────────┘
```
Cards are horizontal, ~200px wide, with a visible portrait frame (initials badge currently), health bar, disposition dot.

### Command Bar

```
┌──────────────────────────────────────────────────────────────────────┐
│ ares> ▌                                                              │
│ ▐ 1 TALK ▌ ▐ 2 BRIBE ▌ ▐ 3 SNEAK ▌ ▐ 4 INSPECT ▌         [EXECUTE]│
└──────────────────────────────────────────────────────────────────────┘
```

The action tabs are framed hardware buttons, always visible, numbered 1-4. They populate the textarea when clicked. EXECUTE is on the far right.

---

## CSS Variables to Use (all defined in `:root`)

```css
--shell-bg: #07101a        /* outer chassis */
--module-bg: #0a1620       /* inset module surface */
--screen-bg: #050b12       /* viewport interior */
--accent-tac-red: #c34a43  /* player / action */
--accent-tac-cyan: #5ea6d6 /* system / scene / nav */
--accent-tac-amber: #c8a24a /* GM / relay */
--accent-tac-green: #63d485 /* ally / friendly */
--font-pixel: "VT323", "Share Tech Mono", monospace
--font-display: "Chakra Petch", "Share Tech Mono", monospace  /* body text */
--unit: 8px
--panel-accent: (per-panel color variable — already hooked into turn-feed, scene, status)
```

The prior CSS section `UI OVERHAUL — PIXEL TERMINAL` (at the very end of `styles.css`) can be kept or replaced in full — it does not conflict with the new work.

---

## Files to Change

### `frontend/src/App.jsx`
- Change the `<main className="layout">` to a 3-column `.main-grid`
- Move `ParticipantStrip` outside `.scene-column`, directly under `.main-grid` as `.presence-bar`
- Move `PlayerInput` outside `.play-column`, directly under `.presence-bar` as `.command-bar`
- Replace `<StatusPanel .../>` with a new `<UtilityColumn .../>` (or refactor StatusPanel to always-visible mode — see below)

### `frontend/src/components/StatusPanel.jsx`
- Remove the icon rail + popout logic
- Render all sub-panels (CharacterPanel, CampaignPanel, MemoriesPanel, ReadinessPanel, SystemPanel) stacked in a single scrollable column, always visible
- Keep sub-panel content the same; just change the wrapper

### `frontend/src/components/PlayerInput.jsx`
- Remove `<ActionBar>` from inside the form
- Accept `actions` prop as before, but render them as a static tab row above (or beside) the textarea
- Action buttons should look like hardware tabs: numbered, bordered, fill textarea on click
- Submit button: keep `frame-cmd-execute` class but integrate properly into the command bar layout

### `frontend/src/components/ActionBar.jsx`
- Rewrite: no popover, no lightbulb trigger
- Render a flat row of framed hardware buttons (up to 4 visible at a time)
- Each shows: `[key]` number, `[label]` text
- On click: calls `onSelectAction(prompt)` — same as before

### `frontend/src/styles.css`
- Strip out any rules in `UI OVERHAUL — PIXEL TERMINAL` that conflict with the new grid
- Add `.main-grid`: `grid-template-columns: minmax(240px, 0.22fr) minmax(0, 0.55fr) minmax(220px, 0.23fr)`
- Add `.feed-column`, `.utility-column` rules
- Add `.presence-bar` — full-width, horizontal scroll if needed
- Add `.command-bar` — full-width, contains action tabs + textarea + execute
- Add `.action-tab-strip` — horizontal flex of `.action-tab` buttons
- Fix panel frame rules to use VISIBLE borders (2-3px, high opacity, not 0.22 opacity)

---

## Priority Order

1. **Layout wireframe** (`App.jsx` + `styles.css` grid rules) — get the 3-column structure rendering at the right proportions first. Use placeholder `<div>` blocks for each region before wiring real components.

2. **Action tabs** (`ActionBar.jsx` + `PlayerInput.jsx`) — replace lightbulb popover with always-visible tab row in the command bar.

3. **StatusPanel always-visible** (`StatusPanel.jsx`) — remove icon rail, render stacked panels in utility column.

4. **Panel visual depth** (`styles.css`) — make borders visible (2-3px, high opacity), add proper title strips, add corner bracket markers that are actually visible.

5. **Turn feed log frames** (`TurnFeed.jsx` + `styles.css`) — each turn card gets the heavy framed treatment with left stripe.

6. **Presence strip** (`ParticipantStrip.jsx` + `styles.css`) — full-width placement, portrait cards with visible HP bars.

---

## What NOT to Change

- Backend: no changes
- API calls: no changes
- State management in App.jsx: no changes (just structural JSX rearrangement)
- Component prop interfaces: keep existing props, just change rendered JSX
- The intro overlay, clarify sidebar — leave untouched
- `docs/layout.md` §"Core Rule": same content, same information — just a different wireframe and real visual depth

---

## Verification

**Hybrid loop:** Use Vite (5173) for CSS-only iteration; rebuild Docker and verify at 5180 for any layout or JSX changes.

After each layout step, rebuild:
```bash
docker compose up --build --no-deps -d frontend
```

Then Playwright (or VS Code Simple Browser) at:
```
URL:      http://localhost:5180/
Storage:  localStorage.ares_intro_seen=1
Viewport: 1366×1024
```

Save screenshots to `assets/samples/ui-iteration/` named `{date}-{slice}-{before|after}.png`.

**Checklist before marking any layout step complete:**
- [ ] Proportions match reference (`assets/samples/ui.png`): narrow feed / wide scene / utility column
- [ ] Panel borders visible at 2-3px, high opacity — not implied by shadow alone
- [ ] Narrative feed readable at normal zoom
- [ ] Command bar and EXECUTE button clearly prominent
- [ ] No regression in topbar, scene bezel, or sidebar assembly (golden-slice panels)
- [ ] `npm run build` passes

Full slice contract and checklist spec lives in `docs/development/workstreams/ui-design-pass.md` §"VS Code Co-Dev Loop".
