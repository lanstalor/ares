# Design: C2 Operator React App

**Date:** 2026-05-06  
**Scope:** Operator-only admin interface for managing campaign hidden state (Objectives, Clocks, Secrets, NPCs, Campaign metadata)  
**Parent:** `~/.claude/plans/a-i-happy-matsumoto.md` — Track C, Slice 2  
**Status:** Ready for implementation

---

## Goal

Provide operators a web-based admin interface (`/admin`) to view and edit campaign hidden state exposed by the C1 operator API, without touching the player-facing game UI.

---

## Architecture

### High-Level Design

- **Route:** Separate `/admin` path lazy-loaded from main `App.jsx`
- **Authentication:** Token-gated via localStorage (no backend validation needed; C1 doesn't require it)
- **Data source:** Single call to `GET /operator/campaigns/{id}/full-state` on mount, stored in React state
- **Mutation:** Individual entities edited via modal forms, submitted as `PATCH /operator/campaigns/{id}/state`
- **Refresh strategy:** Refetch full state after each successful patch to keep UI in sync

### Why This Approach

- Leverages existing C1 API without adding complexity
- Sidebar nav + modal editors are familiar admin UX patterns
- Single data source (full state) prevents data inconsistency
- Isolated route keeps operator concerns separate from player UI
- Easy to extend for C3/C4 (lore authoring, session prep, continuity review)

---

## Routing & Authentication

### Token-Gating Flow

1. User navigates to `/admin`
2. `AdminApp.jsx` checks `localStorage.ares_operator_token`
3. If missing/empty: show `AdminLogin.jsx` (single input field + submit button)
4. On login submit: store token in localStorage, attempt to load full state
5. If full state load fails (401/403 or network error), show error and clear token
6. On success: load sidebar nav + entity pages
7. Logout button clears localStorage and redirects to `/`

### Token Header

All operator API calls include:
```
Authorization: Bearer {token}
```

---

## Component Structure

### Directory Layout

```
frontend/src/admin/
├── AdminApp.jsx              # Main app router, sidebar, full-state context
├── AdminLogin.jsx            # Token input form
├── pages/
│   ├── CampaignPage.jsx      # View/edit campaign metadata
│   ├── ObjectivesPage.jsx    # Objectives table + modal editor
│   ├── ClocksPage.jsx        # Clocks table + modal editor
│   ├── SecretsPage.jsx       # Secrets table + modal editor
│   └── NPCsPage.jsx          # NPCs table + modal editor
├── components/
│   ├── AdminSidebar.jsx      # Left nav (objectives, clocks, secrets, NPCs, campaign)
│   ├── EntityTable.jsx       # Generic table for any entity list
│   └── EntityModal.jsx       # Generic form modal for editing
└── hooks/
    └── useOperatorApi.js     # API client (getFullState, patchState, getAudit)
```

### Data Flow

```
AdminApp (loads full state)
  ├─ AdminSidebar (shows nav options)
  ├─ CampaignPage / ObjectivesPage / etc. (displays entity lists)
  │  └─ EntityTable (renders rows, onClick → EntityModal)
  │     └─ EntityModal (form with pre-filled values)
  │        └─ useOperatorApi.patchState() → refetch full state
```

---

## Entity Editors (MVP Scope)

### 1. Campaign Metadata (`CampaignPage`)

**Fields:**
- `name` (text) — campaign title
- `tagline` (text) — public campaign premise
- `current_date_pce` (number) — in-game date
- `current_location_label` (text) — where Davan is

**Presentation:** Single form (not a table; only one campaign per app context)

### 2. Objectives (`ObjectivesPage`)

**Table columns:** title, is_active, is_complete  
**Edit fields:** title, description, gm_instructions, is_active, is_complete

**Justification:** Operators frequently update active objectives mid-campaign; GM instructions are hidden from player and must be editable.

### 3. Clocks (`ClocksPage`)

**Table columns:** label, clock_type, progress (current/max), hidden_from_player  
**Edit fields:** label, clock_type, current_value, max_value, hidden_from_player

**Justification:** Operators tick clocks and reveal/hide them dynamically; this is core hidden-state mechanic.

### 4. Secrets (`SecretsPage`)

**Table columns:** label, status (sealed/revealed/etc), content_preview  
**Edit fields:** label, content, status, reveal_condition

**Justification:** Secrets are the narrative backbone; operators need to manually reveal, update conditions, or edit content if plot changes.

### 5. NPCs (`NPCsPage`)

**Table columns:** name, disposition, level, current_hp/max_hp  
**Edit fields:** All of the above (inline or modal)

**Justification:** Quick HP/disposition patches during/between turns. Level can be tweaked if campaign difficulty shifts.

---

## API Integration

### useOperatorApi Hook

```javascript
// hooks/useOperatorApi.js
export function useOperatorApi() {
  const token = localStorage.getItem('ares_operator_token');

  return {
    async getFullState(campaignId) {
      const res = await fetch(`/api/v1/operator/campaigns/${campaignId}/full-state`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`Full state fetch failed: ${res.status}`);
      return res.json();
    },

    async patchState(campaignId, updates) {
      const res = await fetch(`/api/v1/operator/campaigns/${campaignId}/state`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      if (!res.ok) throw new Error(`Patch failed: ${res.status}`);
      return res.json();
    },

    async getAudit(campaignId) {
      const res = await fetch(`/api/v1/operator/campaigns/${campaignId}/audit`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`Audit fetch failed: ${res.status}`);
      return res.json();
    }
  };
}
```

### Full State Lifecycle

1. **On AdminApp mount:** Fetch full state, store in React Context (OperatorStateContext)
2. **On entity edit:** User fills form, submits
3. **On patch success:** Refetch full state, update context, close modal, show success toast
4. **On patch failure:** Show error toast, keep modal open, user can retry

### Error Handling

- Network errors: Toast notification + option to retry
- 401/403 (token invalid): Clear localStorage, redirect to login
- 4xx/5xx (server error): Toast showing HTTP status + message from backend
- Validation errors: Display inline in form fields if backend includes field-level errors

---

## UI/UX Details

### Login Screen

- Centered card with:
  - Text input for "Operator Token"
  - Submit button
  - Info text: "Paste your ARES_OPERATOR_TOKEN to continue"
- On token submit, attempt to load full state; show loading spinner
- If load fails, show error message and allow retry

### Sidebar Navigation

- Left sidebar, fixed width (~200px)
- Menu items: Campaign, Objectives, Clocks, Secrets, NPCs
- Active item highlighted
- Logout button at bottom

### Entity Tables

- Standard table with sortable headers (optional for MVP, but implement sorting for at least one column)
- Click row to open editor modal
- Delete button per row (optional for MVP; confirm dialog if implemented)
- Refresh button to manually sync state from server

### Entity Modal Forms

- Modal overlay with form fields matching entity schema
- Submit and Cancel buttons
- Show loading state during patch
- On success: close modal, show toast, refresh parent table
- On error: show inline error message, keep modal open for retry

### Accessibility

- Semantic HTML (use `<button>`, `<label>`, proper form structure)
- ARIA labels on form inputs
- Keyboard navigation (Tab to move between fields, Enter to submit)

---

## Testing Strategy

### Unit Tests (Jest + React Testing Library)

- `useOperatorApi()` — mock fetch, verify correct endpoints and headers
- `EntityTable.jsx` — renders rows, click triggers callback
- `EntityModal.jsx` — form validation, submit calls handler with correct payload
- `AdminSidebar.jsx` — renders nav items, active state, logout clears token

### Integration Tests

- Full flow: Login → view full state → edit objective → see updated state
- Error handling: Failed patch shows error, modal stays open

### Manual Testing

- Test on Docker compose at http://localhost:5180/admin
- Verify token persistence across page reload
- Verify logout clears token and redirects to login
- Test each entity editor (objectives, clocks, secrets, NPCs)
- Test network error handling (disconnect backend, try to patch)

---

## Implementation Roadmap

### Phase 1: Foundation (Routes, Auth, API Client)
1. Add `/admin` route to `App.jsx` (lazy load AdminApp)
2. Build `AdminLogin.jsx` (token input, localStorage save)
3. Build `useOperatorApi()` hook
4. Build `AdminApp.jsx` (loads full state, provides context, shows sidebar)

### Phase 2: Navigation & Campaign Page
5. Build `AdminSidebar.jsx` (nav menu)
6. Build `CampaignPage.jsx` (view/edit campaign metadata)
7. Test token-gating and full-state load

### Phase 3: Entity Pages (Objectives, Clocks, Secrets, NPCs)
8. Build `EntityTable.jsx` (reusable table component)
9. Build `EntityModal.jsx` (reusable form component)
10. Build `ObjectivesPage.jsx`, `ClocksPage.jsx`, `SecretsPage.jsx`, `NPCsPage.jsx`
11. Wire up patch logic for each entity type

### Phase 4: Polish & Testing
12. Error handling (toasts, 401 redirect, validation messages)
13. Loading states (spinners during fetch/patch)
14. Unit tests for hooks and components
15. Manual testing at 5180

---

## Constraints & Assumptions

- **Single operator per campaign** — No multi-user locking or conflict resolution needed
- **Token stored in localStorage** — Acceptable for single-operator product; not production-grade
- **C1 API is authoritative** — UI doesn't cache or predict; always refetch after mutations
- **No new backend changes** — This slice is 100% frontend; reuses C1 endpoints as-is
- **Feature-flagged** — Will add `ARES_ENABLE_ADMIN` env var and hide `/admin` link from player UI if flag is off

---

## Success Criteria

- [ ] `/admin` route loads without errors (token-gated)
- [ ] Can view campaign metadata, objectives, clocks, secrets, NPCs
- [ ] Can edit any entity and see changes reflected immediately in the table
- [ ] Token persists across page reload; logout clears it
- [ ] Network errors are handled gracefully (no silent failures)
- [ ] `make check` passes (no TypeScript/ESLint errors)
- [ ] Playwright screenshot at 5180 shows admin UI at 1366×1024 and 390×844
- [ ] All hard constraints respected (no player-facing leaks, etc.)

