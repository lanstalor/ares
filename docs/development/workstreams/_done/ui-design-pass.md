# Workstream: UI Design Pass — Containers, Frames, and Asset Slots

## Goal

Transform the current flat terminal UI into a physically-grounded instrument-panel aesthetic. Every major section gets a proper enclosure frame. Where visual assets (AI-generated imagery, Illustrator-crafted chrome elements) are planned, the CSS establishes a **slot** — a defined container with placeholder styling — so assets can drop in without structural changes to the markup.

This is a **two-phase** workstream:

- **Phase 1 (CSS pass):** Implement all structural frames and containers using pure CSS. Slots are visible as styled placeholders.
- **Phase 2 (Asset generation):** Fill each slot with the real asset. No HTML changes required — just drop the file into the right path and remove the placeholder CSS.

---

## Design Direction

**"Salvaged Military Rack"** — The UI reads like a cobbled-together instrument console aboard a lowRed mining station. Individual sections are physical modules bolted into a rack, each with:

- An inset border (1–2px, low-opacity accent color)
- A colored top-edge strip that labels the module type
- Corner bracket markers on key panels (`┌─` / `─┐` style via CSS pseudo-elements)
- Subtle inner shadow to create depth and enclosure
- Header rows that look like labeled selector tabs, not div headings

The goal is not a redesign. The dark palette, grid background, Chakra Petch / Share Tech Mono fonts, and cyan/gold accent language all stay. We are adding the **physical frame layer** that makes sections feel like hardware modules, not floating text blocks.

---

## Asset Inventory

Each asset has a **slot name** (CSS class / file path convention), a **spec**, and a **placeholder strategy**.

### A. Panel Chrome — Corner Piece SVGs

| Slot | Description | Size | Format | Placeholder |
|---|---|---|---|---|
| `panel-corner-tl` | Top-left corner bracket, key panels | 24×24px | SVG | CSS `::before` border lines |
| `panel-corner-tr` | Top-right corner bracket | 24×24px | SVG | CSS `::after` border lines |

**Aesthetic brief:** Industrial corner bracket — think targeting reticle or riveted metal. Thin strokes, accent cyan color, transparent fill. Should work as `mask-image` or inline SVG. One design, four rotations.

**Where they slot:** `.status-panel`, `.turn-card`, `.scene-metadata-band`

**File path convention:** `frontend/public/chrome/corner-bracket.svg`

---

### B. Background Texture Overlay

| Slot | Description | Size | Format | Placeholder |
|---|---|---|---|---|
| `ui-grain-texture` | Subtle noise/grime overlay, full-page | Tileable ~256×256px | PNG (low-opacity) | CSS `repeating-linear-gradient` noise approximation |

**Aesthetic brief:** Fine noise grain at 3–5% opacity. Think aged CRT phosphor coating or industrial surface grime. Should not read as a pattern — pure organic noise. Generate with Illustrator's roughness effect or Perlin noise.

**Where it slots:** `body::after` or `.app-shell::after`, `position: fixed`, `pointer-events: none`, `opacity: 0.04`

**File path convention:** `frontend/public/chrome/grain.png`

---

### C. Scene Location Art (existing + needed)

Already established at `frontend/public/scene-art/*.png`. Currently 13 images exist. The slot infrastructure is in `SceneBackdrop.jsx`.

**Images needed** (locations in the world bible not yet covered):

| Location Name | Slot filename | Aesthetic brief |
|---|---|---|
| The Melt | `the_melt.png` | Underground molten rock extraction, hellish orange glow, silhouetted workers, industrial scale |
| Lykos Station | `lykos_station.png` | Cramped lowRed habitation block, dim corridors, political graffiti, Jupiter visible through small port |
| Maintenance Deck | `maintenance_deck.png` | (currently falls back to space_docks) — grimy industrial, exposed conduit, fluorescent flicker |
| Copper Admin Hub | `copper_admin.png` | Clinical bureaucratic space, filing systems, low-status Copper officials at desks |
| Surface Relay Tower | `relay_tower.png` | Ganymede exterior, harsh solar radiation shields, communication arrays |

**Size:** Existing images are ~1200×600px dark atmospheric photography style. Match this.

**Format:** PNG or JPEG (JPEG preferred for photographic content, smaller file size)

---

### D. Caste Icons

Small icons for the participant strip and future character displays. Currently the strip uses a two-letter text abbreviation (e.g., "DA" for Davan).

| Slot | Description | Size | Format | Placeholder |
|---|---|---|---|---|
| `caste-icon-red` | lowRed caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-gold` | Gold caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-copper` | Copper caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-gray` | Gray caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-obsidian` | Obsidian caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-blue` | Blue caste mark | 20×20px | SVG | Colored circle with letter |
| `caste-icon-silver` | Silver caste mark | 20×20px | SVG | Colored circle with letter |

**Aesthetic brief:** Abstract geometric sigil, not literal letters. Think heraldic mark simplified to a minimal glyph. Each caste has its own geometric motif. Monochrome — color comes from CSS `color` property so they adapt to dark/light contexts.

**File path convention:** `frontend/public/chrome/caste/red.svg`, `gold.svg`, etc.

**Where they slot:** `.participant-avatar`, `.turn-label-caste`, `.status-grid dt[data-caste]`

---

### E. ARES Logotype / Wordmark

| Slot | Description | Size | Format | Placeholder |
|---|---|---|---|---|
| `ares-wordmark` | Custom lettering for the topbar brand | ~120×32px | SVG | Current `<h1>ARES</h1>` Chakra Petch text |

**Aesthetic brief:** Industrial stencil lettering with deliberate imperfection — think stamped metal plate. Slightly distressed, no rounded corners. Should read as "ARES" but feel like a physical stamp, not a font render.

**File path convention:** `frontend/public/chrome/ares-wordmark.svg`

**Where it slots:** `.topbar-brand h1` — replace text content with `<img>` when ready.

---

## Phase 1: CSS Pass — Implementation Plan

The following changes are CSS-only. No asset files required.

### 1. Panel enclosure system

Add to `styles.css`:

```css
/* Base panel frame — applied to .status-panel, .turn-card, major layout sections */
.panel-frame {
  position: relative;
  border: 1px solid rgba(72, 92, 94, 0.5);
  background: rgba(7, 12, 16, 0.85);
  box-shadow: inset 0 1px 0 rgba(94, 166, 214, 0.08), 0 2px 12px rgba(0,0,0,0.4);
}

/* Colored top-edge strip — color set by modifier class */
.panel-frame::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--panel-accent, var(--border-strong));
}

/* Corner bracket markers — top-left and top-right */
.panel-frame::after {
  content: '';
  position: absolute;
  top: -1px; left: -1px; right: -1px;
  height: 8px;
  /* Simulated corner notches via border */
}

/* Modifier: accent colors by panel type */
.panel-frame--system  { --panel-accent: var(--accent-friendly-blue); }
.panel-frame--status  { --panel-accent: var(--accent-gold); }
.panel-frame--feed    { --panel-accent: var(--terminal-green); }
.panel-frame--alert   { --panel-accent: var(--bad); }
.panel-frame--secret  { --panel-accent: #c084fc; }
```

### 2. Grain texture placeholder (until real texture asset is ready)

```css
.app-shell::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  /* Placeholder: CSS noise approximation. Replace with url('/chrome/grain.png') when asset exists */
  background-image: url("data:image/svg+xml,..."); /* generated noise SVG */
  opacity: 0.035;
  z-index: 9999;
}
```

### 3. Turn card enclosures

Each `.turn-card` (or `.turn-gm`, `.turn-player`) gets the panel-frame treatment with a left border accent that matches the speaker.

### 4. Layout column frames

The three main columns (`.play-column`, `.scene-column`, `.status-stack`) each get a subtle outer border to visually separate them from the background.

### 5. Caste icon placeholders

The participant avatar (`DA`, `AR` etc.) gets a structured slot:

```css
.participant-avatar {
  /* When caste icon asset exists: use as background-image */
  /* Placeholder: current letter-in-box approach */
  background-image: var(--caste-icon-url, none);
}
```

---

## File Paths for All Assets

When generating assets, drop them here — no code changes required:

```
frontend/public/
├── chrome/
│   ├── corner-bracket.svg     # Panel corner piece
│   ├── grain.png              # Background texture overlay
│   ├── ares-wordmark.svg      # Topbar logotype
│   └── caste/
│       ├── red.svg
│       ├── gold.svg
│       ├── copper.svg
│       ├── gray.svg
│       ├── obsidian.svg
│       ├── blue.svg
│       └── silver.svg
└── scene-art/                 # Already exists
    ├── the_melt.png           # NEEDED
    ├── lykos_station.png      # NEEDED
    ├── maintenance_deck.png   # NEEDED
    ├── copper_admin.png       # NEEDED
    └── relay_tower.png        # NEEDED
```

---

## Phase 2: Asset Drop-In

When each asset is ready:

1. **Corner bracket SVG:** Replace CSS pseudo-element placeholders with `mask-image: url('/chrome/corner-bracket.svg')` on `.panel-frame::before` and `::after`.
2. **Grain texture:** Replace the inline SVG data URI in `.app-shell::after` with `url('/chrome/grain.png')`.
3. **Scene art:** Drop into `frontend/public/scene-art/` — `SceneBackdrop.jsx` already maps location labels to filenames.
4. **Caste icons:** Set `--caste-icon-url` CSS variable per caste class on `.participant-avatar`.
5. **ARES wordmark:** Replace `<h1>ARES</h1>` with `<img src="/chrome/ares-wordmark.svg" alt="ARES" />` in `App.jsx`.

No structural HTML/JSX changes required for any of these drops.

---

## Current State

- Phase 1 (CSS pass): **Complete** (2026-04-30)
- Icon sidebar refactor: **Complete** (2026-04-30)
- Phase 2 (Asset generation): **Superseded — see UI Overhaul workstream**

## Phase 1 Implementation Notes

All Phase 1 changes are in `frontend/src/styles.css` at the bottom, under the "PANEL FRAME SYSTEM" section.

What was implemented:
- `--panel-accent` CSS custom property drives the top-edge strip per panel type
- Green → turn feed, command line (narrative); cyan/blue → topbar, scene, participants (system); gold → status panel
- `border-top: 2px solid var(--panel-accent, ...)` on all major panels — overrides the base 1px top border
- `.scene-backdrop-panel` and `.participant-strip` use `color-mix(... var(--scene-accent) ...)` so accent strips track scene tone changes
- `.app-shell::after` — SVG turbulence noise grain at 3.8% opacity, `mix-blend-mode: overlay` (Phase 2 replaces with `/chrome/grain.png`)
- `.participant-portrait` — `background-image: var(--caste-icon-url, none)` slot ready for Phase 2 SVG icons
- `.mode-live .play-column::after` — faint vertical separator between play and status columns

Corner bracket markers are provided by the existing `clip-path: polygon(...)` notch on all panels — no new pseudo-elements needed.

## Icon Sidebar Implementation Notes (2026-04-30)

Replaced the always-visible status panel column with a 56px icon rail + popout overlay system.

**Layout change:** `.mode-live .layout` column reduced from `minmax(240px, 320px)` to `56px`. The play column and scene column now have full remaining width.

**Scene backdrop:** `aspect-ratio: 4/3` enforced on `.mode-live .scene-column .scene-backdrop-panel` (was `flex: 1`). Width drives height.

**StatusPanel.jsx rewrite:**
- `useState(null)` tracks active tab id; null = collapsed
- 5 tabs: `◈` Field Readout, `◎` Current Brief, `◉` Campaign Log, `⊙` GM Stack, `⊞` Machine State
- Each section extracted into its own component (CharacterPanel, CampaignPanel, MemoriesPanel, ReadinessPanel, SystemPanel)
- `.sidebar-icon-rail` — 56px flex column of icon buttons with gold accent strip
- `.sidebar-popout` — `position: absolute; right: 56px; top: 0; bottom: 0; width: 300px` — overlays the scene when active
- Clicking active icon collapses the popout (toggle)

**CSS additions** (end of `styles.css`): `.sidebar-icon-rail`, `.sidebar-icon-btn`, `.sidebar-icon-btn.is-active`, `.sidebar-popout`, `.sidebar-popout .status-panel`.

## UI Overhaul Implementation (2026-04-30)

**Status: Golden-slice CSS refactor complete.** Implements the pixel-art rebel terminal aesthetic from `docs/layout.md` and `assets/samples/ui.png`. All Phase 1 styling (top-edge accents + clip-path notches) preserved on untouched panels so the UI never looks half-dressed during rolling refactor.

**Delivered (all merged to main, commit 0252225):**
- Design tokens: `--shell-bg`, `--shell-bevel-*`, `--module-*`, `--screen-*`, `--accent-tac-*`, `--unit` grid
- VT323 font loaded for pixel-style labels and tabs
- Frame primitives (all CSS-only, asset-swappable): `.frame-shell`, `.frame-module`, `.frame-screen`, `.frame-cmd`, `.frame-chip`
- Applied to golden slice:
  * `.topbar` — cyan stripe, pixel ARES wordmark, VT323 labels (TIME/SIGNAL/RUNTIME/etc), quieter contrast
  * `.input-panel.frame-cmd` — red top stripe, taller housing (78px min), hardware-style EXECUTE button (bevelled, embossed, pressable), focus-state cyan glow halo
  * `.scene-backdrop-panel.frame-screen` — monitor bezel with inset surface, scanline overlay
  * `.sidebar-icon-rail.frame-module` + `.sidebar-popout.frame-module` — folded into chassis as one bolted assembly (amber stripe, flush edge, no shadow gap when open, active button shows side-accent)
  * `.frame-shell` on `.app-shell` — outer chassis bevel (top/left highlight, bottom/right shadow) + corner rivets
- Hierarchy: older `.turn-item` entries fade via `:nth-last-child` opacity ramp (oldest 55%, middle 78%, newest 100%)
- Asset hooks ready (no markup edits needed): `--shell-frame-image`, `--module-frame-image`, `--screen-frame-image`, `--cmd-frame-image`, `--ares-wordmark`

**Screenshots (iPad Pro landscape 1366×1024):**
- `ui-overhaul-golden-slice.png` — full collapsed state (icon rail, scene, command line)
- `ui-overhaul-popout-open-v2.png` — popout open (sidebar-popout flush against rail)

**Out of scope (follow-up passes):**
- Turn feed, participant strip, action bar, status panel interior reskinning (still on Phase 1 styling)
- Asset generation (corner brackets PNG/SVG, grain texture, ARES wordmark, caste icons, scene art)
- New panels or IA changes

## Next Step

Reskin remaining panels (turn feed → embedded system log, participant strip → tactical dossier chips, action bar → hardware toggles) with the same frame primitives. All asset hooks already in place per the asset-drop pattern.

---

## VS Code Co-Dev Loop

This section is the canonical process for all UI-iteration work on this slice. Read and follow it at the start of every co-dev session.

### Environment decision by change type

| Change type | Loop | Port |
|---|---|---|
| CSS-only (colours, spacing, font weight, no layout) | `make frontend-dev` — Vite HMR, no rebuild needed | 5173 |
| Layout / JSX structural / anything touching state or API | Full stack already running — `docker compose up --build --no-deps -d frontend` after each batch of changes | 5180 |

**Canonical test URL:** `http://localhost:5180/`  
Skip intro: set `localStorage.ares_intro_seen=1` in the browser console before screenshotting.

### Visual aids in VS Code

1. **VS Code Simple Browser** — keep open at `http://localhost:5173` (Vite) for live watching during CSS edits. Switch to `http://localhost:5180` when validating layout-level changes.
2. **Playwright MCP** — use for durable checkpoint captures at the end of each slice. Screenshots are the evidence record, not optional.

### Slice contract

Every UI slice must define the following before work begins:

```
Goal:         <one sentence, one visual objective>
Scope in:     <explicit list of files / components>
Scope out:    <explicit exclusions to prevent scope creep>
Exit criteria:<list of checklist items that must pass>
```

### Verification checklist (run at each slice boundary)

Capture a Playwright screenshot at **1366×1024** on port **5180** after rebuilding. Store it in `assets/samples/ui-iteration/` named `{YYYY-MM-DD}-{slice-name}-{before|after}.png`. Then manually compare against the previous checkpoint and the target reference (`assets/samples/ui.png`).

- [ ] Layout hierarchy: feed column narrow, scene dominant, utility always-visible
- [ ] Narrative feed readable at normal reading distance (text not competing with frame chrome)
- [ ] Command bar prominent — EXECUTE visible and affordance clear
- [ ] Scene backdrop visible and not obscured by overlay panels
- [ ] Panel borders visible (not washed out) — depth is real, not implied
- [ ] No regression in existing golden-slice panels (topbar, command line, scene bezel, sidebar assembly)
- [ ] No hidden-state data in player-visible UI
- [ ] `npm run build` passes with no errors before checkpoint is recorded

### Handoff evidence (required before pausing or switching agents)

Add to the workstream doc under a **"Last verified"** heading:

```
Last verified: {date}
Before screenshot: assets/samples/ui-iteration/{file}
After screenshot:  assets/samples/ui-iteration/{file}
Checklist result:  all pass | <list any fails>
Known visual debt: <describe anything left undone>
Next slice:        <exact goal sentence for the next session>
```

---

## Last Verified

```
Last verified: 2026-05-01
Before screenshot: assets/samples/ui-iteration/2026-05-01-baseline-before.png
After screenshot:  (none yet — this is the opening baseline)
Checklist result:  n/a — baseline capture only, no changes applied yet
Known visual debt: Turn feed cards, participant strip, action bar, and status panel interiors
                   still have Phase 1 (accent strip only) styling — not yet given frame-module treatment
Next slice:        Reskin the turn feed into a framed embedded system log — each turn card gets
                   visible 2px border, left-stripe speaker accent, source badge, and timestamp chip
```
