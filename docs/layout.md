# ARES UI Refactor Instructions

## Goal

Take the current UI screenshot as the structural/layout baseline and transform it into the pixel-art diegetic rebel terminal style shown in the target concept. Preserve the usability and screen organization of the current interface while changing the visual language so it feels like a physical, in-world Ares command terminal.

This document can be given to Codex, Claude, or another implementation assistant.

---

## Inputs

### Image A — Current State
Use the supplied current screenshot as the source of truth for layout.

Interpret Image A as containing these major regions:

- Top header / status bar
- Left narrative feed
- Large center scene viewport
- Bottom scene presence strip
- Bottom command line + execute area
- Right-side utility / chrome controls

### Target Outcome
The target is the generated pixel-art rebel terminal example.

Interpret that target as:

- Pixel-art interface language
- Thick industrial frames
- Inset screens and monitor bezels
- Dark teal / blue-black shell
- Red/orange tactical data accents
- Cyan system accents
- Readable but gritty military/rebel tone
- Diegetic, in-world console rather than clean web dashboard

---

## Core Rule

Do not redesign the information architecture.

Keep the current screen structure and relative placement of major regions from Image A. The work is primarily:

1. Reskinning
2. Hierarchy correction
3. Component redesign
4. Asset system planning

The result should feel like the same UI upgraded into a pixel-art Ares terminal.

---

## High-Level Design Intent

The finished interface should feel like:

- A stolen Society terminal
- Modified and repurposed by the Sons of Ares
- Slightly degraded but reliable
- Utilitarian, tense, and information-dense
- Visibly physical, as if made of bolted monitors and embedded control modules

The finished interface should avoid:

- Modern SaaS styling
- Clean glassmorphism
- Generic neon cyberpunk
- Glossy consumer tablet styling

---

## What to Preserve from Image A

Preserve these structural strengths from the current design:

- Strong left-to-right reading order
- Narrative feed on the left
- Large central scene panel
- Compact scene presence strip below the viewport
- Command line anchored at the bottom
- Top status strip for metadata

Also preserve the current feature set:

- Narrative feed entries
- Active/current moment card
- Scene tabs
- Scene title and objective
- Presence cards
- Command line and execute button

---

## What to Change

### 1. Convert the Whole Interface into a Physical Terminal Shell

The current UI looks like flat software panels. Change it so the interface appears mounted inside a physical machine.

Add:

- Thick outer frame around the whole screen
- Beveled or chamfered corners
- Inset monitor-like panels
- Visible border depth
- Small decorative technical housings or micro-panels at edges
- Subtle hardware-like modularity

Every major region should look embedded in a larger terminal chassis.

---

### 2. Change the Visual Language to Pixel-Art Tactical UI

Convert the current crisp sci-fi UI to a pixel-art direction:

- Hard 1-2 px edge styling
- Pixel font for labels, tabs, metadata, and small system text
- Readable low-res UI iconography
- Slight scanlines or dithering
- Light CRT/monitor texture where helpful
- Subtle noise and wear

Do not overdo degradation. The interface must remain readable.

---

### 3. Strengthen the Hierarchy

The current UI is clean, but the target look needs more deliberate emphasis.

Visual hierarchy should be:

#### Primary

- Command line
- Current scene/viewport
- Most recent narrative content
- Current objective

#### Secondary

- Scene presence strip
- Tabs
- Active character information

#### Tertiary

- Top metadata
- Side chrome
- Decorative status widgets
- Low-priority utility readouts

This means:

- The command line should become more visually prominent
- The center viewport should remain dominant
- Older narrative entries should recede slightly
- Decorative chrome must not compete with gameplay information

---

### 4. Replace Flat Panels with Modular Framed Panels

All current panels should be reworked into a consistent framed style.

Each panel should generally have:

- Outer metal frame
- Inner inset content area
- Optional title bar
- Optional status accent line
- Dark content surface
- Subtle interior grid or monitor texture

Create a shared panel grammar so the UI looks like one system.

Panel classes to support:

- Header panel
- Narrative panel
- Current moment panel
- Viewport panel
- Map/minimap panel
- Presence chip/card panel
- Command line panel
- Utility/status panel
- Modal panel
- Tab/button panel

---

### 5. Upgrade the Command Line

The command line is the most important interaction surface and should be visually upgraded.

Required changes:

- Make it taller and more obvious
- Give it a strong frame
- Add a blinking cursor
- Add hardware-console flavor
- Make the execute button feel like a physical action control
- Add subtle active/focus glow or pulse

Suggested states:

- Idle
- Focused
- Typing
- Executing
- Blocked
- Compromised

Action buttons, if shown, should look like hardware toggles or inset control pads rather than simple web buttons.

---

### 6. Rework the Narrative Feed into an Embedded System Log

The left narrative feed should still feel textual and story-forward, but look more like a machine log.

Change it by:

- Adding stronger framed message containers
- Using faction or source accent colors sparingly
- Making the latest/active item more prominent
- Fading older items slightly
- Using pixel-style timestamps and labels
- Keeping long-form text readable by not over-stylizing paragraph content

Color coding suggestions:

- Player / operative: muted red
- System: cyan
- Ares / GM / relay: amber
- Hostile or danger: orange-red

---

### 7. Rework the Center Scene Area

The center scene region should become a framed monitor viewport.

Keep:

- Tabs
- Environment label
- Scene title
- Objective area
- Scene tone / connection area

Change:

- Wrap the viewport in a thick monitor frame
- Darken the scene art slightly for text legibility
- Make the scene label and title look like terminal overlays
- Put objective and scene tone in small inset panels below or inside the viewport frame
- Reduce the airy, flat feel of the current panel

The scene should feel like a live feed on a console screen.

---

### 8. Rework the Scene Presence Strip

The current scene presence strip should become a row of tactical dossier chips.

Each chip should support:

- Small portrait or initials badge
- Level or rank marker
- Name
- Role
- Affiliation/friendliness tag
- Health or status bars

These should stay compact but more tactile and pixel-framed.

---

### 9. Rework Top Bar and Side Controls

The top bar should remain, but shift into the pixel-hardware style.

It should contain:

- Brand / ARES identity
- Location breadcrumb
- Time / signal / runtime
- Tone mode
- Optional help/audio/system controls

The right-side utility rail can remain, but must be restyled to look integrated into the shell.

Make these controls visually quieter than the main gameplay areas.

---

## Style Guide

### Palette
Use a restrained palette with semantic roles.

#### Base shell

- Deep teal
- Blue-black
- Dark steel

#### Text

- Soft off-white
- Muted gray-blue
- Low-contrast system labels

#### Functional accents

- Muted industrial red for primary action / danger / player emphasis
- Cyan for system / neutral machine information
- Amber for relay / warning / Ares comms
- Green for ally/friendly signals

Avoid rainbow cyberpunk color use.

### Texture
Use subtle:

- Scanlines
- Grid overlays
- Pixel noise
- Minor edge wear
- CRT-like signal texture on some inset screens

### Typography
Use two font modes:

#### Pixel display font
For:

- Titles
- Labels
- Tabs
- Status text
- Metadata

#### Readable body font or cleaner pixel-compatible font
For:

- Narrative paragraphs
- Command input content
- Longer descriptions

If only one font is practical, choose one that remains readable at small sizes.

---

## Constraints for the Refactor

### Must keep

- Current overall layout structure from Image A
- Current content regions
- Current interaction model
- Readability of narrative and objective text

### Must change

- Borders
- Panel construction
- Button style
- Tab style
- Command line style
- Top bar style
- Presence card style
- Surface textures and chrome
- Typography to a more pixel/tactical direction

### Must avoid

- Adding too many new panels
- Overcomplicating the current layout
- Making all areas equally loud
- Sacrificing text legibility for visual style

---

## Asset Production Assumption

Assume this project will require dozens of image assets in specific dimensions to support the final UI.

Because of that, the implementation should be based on a modular asset system, not one-off full-screen art.

The correct approach is:

1. Define the design system
2. Create reusable asset primitives
3. Create dimensional variants
4. Assemble screens from those pieces

---

## Recommended Asset Strategy

### 1. Use a Base Unit Grid

Pick a base unit early, for example:

- 8 px grid for layout
- 2 px or 4 px visual increments for pixel details

All assets should align to this unit system.

This will make it far easier to generate many UI assets consistently.

---

### 2. Use 9-Slice / Modular Framing Wherever Possible

Do not generate a unique full-frame border for every component.

Instead create:

- Corners
- Edges
- Center fills
- Header bars
- Divider modules

This allows scalable framed panels without repainting each size manually.

Core reusable frame assets:

- Outer frame corners
- Outer frame edges
- Inner frame corners
- Inner frame edges
- Panel fill texture
- Title bar strip
- Divider strip
- Status accent strip

---

### 3. Separate Asset Categories

Organize production into categories.

#### A. Structural assets
Used everywhere.

- Outer shell frame
- Panel frames
- Card frames
- Tab frames
- Button frames
- Divider lines
- Content backgrounds

#### B. Utility overlays

- Grid overlays
- Scanline overlays
- Noise overlays
- Glow masks
- Signal distortion overlays

#### C. Iconography

- Action icons
- Status icons
- System icons
- Faction icons
- Map markers

#### D. Content-holder assets

- Portrait frames
- Stat bar frames
- Mini-screen frames
- List row frames
- Tooltip / modal frames

#### E. Decorative hardware assets

- Bolts / rivets
- Micro-panels
- Vents
- Indicator lights
- Warning stripes

---

## Recommended Folder Structure

```text
/assets
  /ui
    /shell
    /panels
    /cards
    /buttons
    /tabs
    /dividers
    /overlays
    /textures
  /icons
    /actions
    /status
    /factions
    /map
    /system
  /portraits
  /backgrounds
  /scene-viewports
  /maps
  /fx
  /fonts
```

---

## Naming Convention

Use deterministic names. Example:

```text
ui_panel_frame_default_320x180.png
ui_panel_frame_active_320x180.png
ui_button_primary_idle_160x40.png
ui_button_primary_hover_160x40.png
ui_tab_selected_120x32.png
ui_tab_unselected_120x32.png
ui_presence_card_friendly_240x72.png
ui_commandline_frame_1024x56.png
ui_overlay_scanline_subtle_2048x1536.png
```

For modular parts:

```text
ui_panel_corner_tl_default.png
ui_panel_corner_tr_default.png
ui_panel_edge_top_default_8px.png
ui_panel_fill_default_tile_8px.png
```

---

## Required Asset Families

Below is the minimum family list to plan for.

### Shell and frame assets

- Full screen shell frame
- Inner shell shadow / inset layer
- Generic panel frame
- Active panel frame
- Warning panel frame
- Small utility panel frame
- Modal frame

### Header assets

- Top bar segments
- Brand plate
- Metadata capsule
- Tone/audio/help button frames

### Panel title assets

- Title strip default
- Title strip active
- Title strip warning
- Label chips

### Buttons and tabs

- Primary button idle / hover / active / disabled
- Secondary button idle / hover / active / disabled
- Execute button variants
- Tab selected / unselected / hover
- Micro-button icons

### Command line assets

- Command line frame
- Left prompt block
- Cursor sprite
- Status indicator block
- Execute module
- Warning/blocked overlay

### Narrative assets

- Feed item frame
- Current moment card
- Message source badge
- Timestamp chip
- Scroll bar frame

### Presence assets

- Portrait frame small
- Portrait frame medium
- Presence card base
- Relationship tag chips
- Health bar shell
- Health bar fill variants
- Level badge

### Status assets

- Stat bars
- Telemetry chart frames
- Progress bars
- Alert lights
- Signal icons
- Encryption chips

### Map assets

- Map node markers
- Route lines
- Highlighted region markers
- Minimap frame
- Legend chips

### Overlays and FX

- Scanline subtle
- Scanline medium
- Signal noise light
- Signal noise heavy
- Vignette light
- Terminal glow mask
- CRT bloom mask

---

## Suggested Standard Dimensions

These do not need to be final, but define a repeatable set.

### Buttons

- Small: 96x32
- Medium: 128x40
- Large: 160x48
- Execute: 176x56

### Tabs

- Compact: 96x28
- Standard: 112x32
- Wide: 128x32

### Presence cards

- Compact: 224x72
- Standard: 256x80
- Wide: 320x80

### Utility panels

- Small: 160x96
- Medium: 240x120
- Standard: 320x180
- Large: 480x240

### Portrait frames

- Icon: 40x40
- Small: 64x64
- Medium: 96x96

### Command line

- Shell: full-width per screen
- Standard height target: 56-72 px

### Full-screen overlays

For iPad Pro landscape concepting, support:

- 2732x2048
- 2048x1536
- 1366x1024 for preview work

---

## Recommended Workflow

### Phase 1 — Lock the Design System
Before generating lots of assets, define:

- Palette
- Typography
- Border language
- Panel frame language
- Grid unit
- Button/tabs style

### Phase 2 — Generate Primitive Assets
Start with only:

- Panel frame set
- Button set
- Tab set
- Command line frame
- Title strip set
- Divider set
- Overlays

### Phase 3 — Build One Golden Screen
Recreate the current UI layout from Image A using only the new pixel assets.

That becomes the canonical layout template.

### Phase 4 — Expand Asset Families
Once the golden screen works, produce:

- Additional button states
- Panel variants
- Status widgets
- Map widgets
- Portrait frames
- Scene tags

### Phase 5 — Produce Content Assets
After the UI kit is stable, create:

- Portraits
- Viewport backgrounds
- Map thumbnails
- Faction icon variants
- Scene-specific overlays

---

## Prompting / Implementation Guidance for Codex or Claude

Use instructions like this:

> Use Image A as the fixed layout baseline. Keep the same major regions and approximate proportions. Replace the flat sci-fi UI language with a pixel-art diegetic rebel terminal style. Build a reusable asset-driven component system so the layout can support dozens of custom image assets in fixed dimensions. Prioritize reusable frames, buttons, tabs, presence cards, overlays, and command-line modules over one-off full-screen art.

Additional instruction:

> Do not add more main panels. Convert the existing interface into a framed embedded-console experience. Preserve usability and text readability. Use an 8 px layout grid and modular assets wherever possible.

---

## Acceptance Criteria

The refactor is successful if:

- The final screen still clearly resembles the current layout from Image A
- The visual language matches the pixel-art rebel terminal concept
- The command line is more prominent and tactile
- The screen feels embedded in a physical console shell
- Text remains readable
- The design system clearly supports scalable production of many future assets

---

## Final Summary

The task is to take the current ARES screen and convert it into a modular, asset-driven, pixel-art command terminal, preserving structure while replacing the visual system.

Treat the current screenshot as the blueprint and the pixel-art concept as the skin, component language, and asset-production model.
