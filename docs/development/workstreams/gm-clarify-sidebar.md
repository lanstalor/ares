# Workstream: GM Clarify Sidebar Chat

## Goal

Add a `?` entry point in the live shell that opens a non-persisted GM sidebar conversation. The backend should explain the current story plainly, break the fourth wall if needed, and must not create a turn or mutate campaign state.

## Scope / Non-goals

- In scope:
  - New backend endpoint `POST /api/v1/campaigns/{id}/clarify`.
  - Frontend sidebar UI for the conversation.
  - "Non-persisted" state (cleared on page refresh or session end).
  - UI entry point (`?` button).
- Out of scope:
  - Persisting these clarification chats to the database.
  - Using clarification chats to influence the game state or character stats.
  - Multi-user support for the sidebar.

## Current State

**Complete — merged to main.**

### Features delivered
- Backend `POST /api/v1/campaigns/{id}/clarify` endpoint.
- `ClarifyEngine` service and `AnthropicNarrationProvider.clarify()` method.
- `ClarifySidebar` React component with markdown rendering (paragraphs, headings, lists, bold/italic).
- Topbar `?` button toggling the sidebar; ESC closes it.
- Sidebar header stays pinned when responses are long (CSS `min-height: 0` + JS `--topbar-height` ResizeObserver fix).
- Clarify system prompt rewritten: no markdown headers, no chatbot endings, brevity-first.

### Also fixed in this branch (GM quality + narrative feed)
- Narrative feed: paragraph breaks now render (split on `\n\n`), bold/italic parsed inline.
- Dialogue coloring: `[Caste]"quote"` renders in caste color; plain quotes render as neutral italic, not gold.
- GM system prompt: pacing discipline, anti-repetition, anti-atmospheric-filler, sentence rhythm guidance.
- Naming conventions added to prompt: Gold `au`, Copper `cu`, etc. "Ares" banned as family name.
- Player character renamed "Davan o' Tharsis" (correct lowRed convention) in world bible, DB, and tests.

## GitHub Links

- Branch: `feat-7-gm-clarify-sidebar`
