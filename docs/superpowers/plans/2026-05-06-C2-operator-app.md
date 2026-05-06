# C2 Operator React App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a token-gated `/admin` route with sidebar navigation, entity tables, and modal editors for managing campaign hidden state (Objectives, Clocks, Secrets, NPCs, Campaign metadata).

**Architecture:** Separate React app at `/admin` route, lazy-loaded from main App.jsx. Single source of truth: full state fetched from C1's `GET /operator/campaigns/{id}/full-state` on mount. Entity edits trigger `PATCH /operator/campaigns/{id}/state`, then full refetch to sync. Token stored in localStorage for persistent authentication.

**Tech Stack:** React 19, React Router 6, Fetch API, TailwindCSS (or existing styles)

**Current directory:** `/home/lans/ares-track-c/C2` (worktree on `track-c/C2-operator-app` branch)

---

## Task 1: Add `/admin` route to App.jsx with lazy loading

**Context:** The main App.jsx is the entry point. We're adding a new route that lazy-loads AdminApp.jsx to keep the main bundle clean.

**Files:**
- Modify: `frontend/src/App.jsx`

### Steps

- [ ] **Step 1:** Add lazy import and Suspense boundary at top of App.jsx (after existing imports)

```jsx
const AdminApp = lazy(() => import('./admin/AdminApp'));
```

Also ensure `lazy` and `Suspense` are imported from React.

- [ ] **Step 2:** Add the /admin route inside the existing `<Routes>` element

```jsx
<Route 
  path="/admin" 
  element={
    <Suspense fallback={<div style={{ padding: '2rem' }}>Loading admin...</div>}>
      <AdminApp />
    </Suspense>
  } 
/>
```

- [ ] **Step 3:** Test in browser at http://localhost:5173/admin — should show "Loading admin..." then blank page (AdminApp doesn't exist yet)

- [ ] **Step 4:** Commit: `git commit -m "feat(C2): add lazy-loaded /admin route"`

---

## Task 2: Create AdminLogin.jsx (token input form)

**Context:** This component handles the token entry screen. It's the gateway to the admin UI.

**Files:**
- Create: `frontend/src/admin/AdminLogin.jsx`

**Component receives props:**
- `onTokenSubmit(token)` - callback when user submits token
- `isLoading` - boolean for loading state
- `error` - string error message

**Component renders:**
- Centered form with "Operator Access" heading
- Text input (type="password") for token
- Submit and Cancel buttons
- Error message display if provided

**Styling:** Use dark theme (matching game UI): #0a0e27 background, #1a1f3a panels, #ff6b35 accent, VT323 font

---

## Task 3: Create useOperatorApi hook with tests

**Context:** This is the API client for talking to C1 operator endpoints. Must include Authorization header with token from localStorage.

**Files:**
- Create: `frontend/src/admin/hooks/useOperatorApi.js`
- Create: `frontend/src/admin/__tests__/useOperatorApi.test.js`

**Hook return object methods:**
- `getFullState(campaignId)` - GET /operator/campaigns/{campaignId}/full-state
- `patchState(campaignId, updates)` - PATCH /operator/campaigns/{campaignId}/state with body
- `getAudit(campaignId)` - GET /operator/campaigns/{campaignId}/audit

**All requests:**
- Include `Authorization: Bearer {token}` header (token from localStorage)
- Throw on non-ok response (401, 404, 500, etc.)

**Tests:** Use vitest/React Testing Library. Test that:
- Authorization header is included
- Correct endpoint is called
- Non-ok responses throw

---

## Task 4: Create AdminApp.jsx (main app, context, full-state load)

**Context:** Main admin component. Handles token-gating, full-state loading, context provider for all admin pages.

**Files:**
- Create: `frontend/src/admin/AdminApp.jsx`

**Functionality:**
- Create `OperatorStateContext` for sharing state across pages
- Export `useOperatorState()` hook for consuming context
- Check localStorage for token on mount
- If no token: show AdminLogin form
- If token exists: call `api.getFullState(campaignId)` on mount
- Store fullState in context and state
- Render sidebar + active page based on state
- Pages: Campaign, Objectives, Clocks, Secrets, NPCs

**Error handling:**
- If full-state fetch fails, show error message with "Back to Login" button
- On 401/403, clear token and redirect to login

**Context provides:**
- `fullState` - the full campaign state object
- `setFullState` - setter for updating after patches
- `campaignId` - derived from URL param or 'default'
- `api` - the useOperatorApi instance

---

## Task 5: Create AdminSidebar.jsx

**Context:** Left sidebar navigation. Shows links to each entity type page.

**Files:**
- Create: `frontend/src/admin/components/AdminSidebar.jsx`

**Props:**
- `activePage` - string (e.g., 'campaign', 'objectives', 'clocks', 'secrets', 'npcs')
- `onPageChange(pageId)` - callback when user clicks menu item
- `onLogout()` - callback for logout button

**Menu items:** Campaign, Objectives, Clocks, Secrets, NPCs

**Styling:** Left sidebar, ~200px wide, #1a1f3a background, #ff6b35 accent, hover effects

---

## Task 6: Create CampaignPage.jsx

**Context:** Edit campaign metadata. Uses AdminApp context to access fullState and api.

**Files:**
- Create: `frontend/src/admin/pages/CampaignPage.jsx`

**Functionality:**
- Display campaign info in a card (non-edit view)
- "Edit" button opens form mode
- Form fields: name, tagline, current_date_pce (number), current_location_label
- "Save" submits via `api.patchState()` with update, then refetches full state
- "Cancel" closes form
- Show loading spinner during save
- Show error message if patch fails

---

## Task 7: Create EntityTable.jsx and EntityModal.jsx (reusable components)

**Context:** Generic components used by all entity pages (Objectives, Clocks, Secrets, NPCs).

**Files:**
- Create: `frontend/src/admin/components/EntityTable.jsx`
- Create: `frontend/src/admin/components/EntityModal.jsx`

**EntityTable props:**
- `entities` - array of objects to display
- `columns` - array of {key, label} objects (which fields to show)
- `onEditRow(entity)` - callback when user clicks Edit
- `onDeleteRow(entity)` - optional callback for delete

**EntityTable renders:**
- Table with headers from columns
- Rows from entities array
- Edit/Delete buttons per row
- Empty state if no entities

**EntityModal props:**
- `isOpen` - boolean
- `title` - string (e.g., "Edit Objective: Find the Relay")
- `entity` - object with current values
- `fields` - array of {name, label, type, options?}
- `onSave(formData)` - async callback
- `onCancel()` - callback
- `isLoading` - boolean for save state
- `error` - string error message

**EntityModal renders:**
- Modal overlay
- Form with fields based on `fields` prop
- Field types: text, number, textarea, checkbox, select
- Save/Cancel buttons
- Error message display

---

## Task 8: Create ObjectivesPage.jsx

**Context:** Table and editor for objectives. Uses EntityTable and EntityModal.

**Files:**
- Create: `frontend/src/admin/pages/ObjectivesPage.jsx`

**Functionality:**
- Fetch objectives from `useOperatorState().fullState.objectives`
- Display in EntityTable with columns: title, is_active, is_complete
- Click Edit → EntityModal with fields: title, description, gm_instructions, is_active, is_complete
- On save: patch with entity_type='objective', entity_id, changes
- Refetch full state on success
- Show errors, loading states

---

## Task 9: Create ClocksPage.jsx

**Context:** Table and editor for clocks.

**Files:**
- Create: `frontend/src/admin/pages/ClocksPage.jsx`

**Functionality:**
- Fetch clocks from fullState.clocks
- Display in EntityTable with columns: label, clock_type, progress (as "current/max"), hidden_from_player
- Click Edit → EntityModal with fields: label, clock_type (select: tension/doom/progress/faction), current_value, max_value, hidden_from_player
- On save: patch with entity_type='clock', entity_id, changes
- Refetch full state on success

---

## Task 10: Create SecretsPage.jsx

**Context:** Table and editor for secrets.

**Files:**
- Create: `frontend/src/admin/pages/SecretsPage.jsx`

**Functionality:**
- Fetch secrets from fullState.secrets
- Display in EntityTable with columns: label, status, content_preview (first 50 chars)
- Click Edit → EntityModal with fields: label, content (textarea), status (select: sealed/revealed/suspected), reveal_condition (textarea)
- On save: patch with entity_type='secret', entity_id, changes
- Refetch full state on success

---

## Task 11: Create NPCsPage.jsx

**Context:** Table and editor for NPCs (non-player characters from fullState.characters).

**Files:**
- Create: `frontend/src/admin/pages/NPCsPage.jsx`

**Functionality:**
- Fetch NPCs from fullState.characters (filter out player character)
- Display in EntityTable with columns: name, disposition, level, hp (as "current/max")
- Click Edit → EntityModal with fields: name, disposition (select: allied/neutral/hostile/unknown), level, current_hp, max_hp
- On save: patch with entity_type='character', entity_id, changes
- Refetch full state on success

---

## Task 12: Add admin-specific styles to frontend/src/styles.css

**Context:** CSS for admin UI. Append to existing styles.css.

**Files:**
- Modify: `frontend/src/styles.css`

**Styles needed:**
- Admin layout (sidebar + main area)
- Sidebar styling and hover states
- Table styling (headers, rows, action buttons)
- Modal overlay and modal styling
- Form inputs and buttons
- Loading spinners, error messages

---

## Task 13: Test full admin app flow at http://localhost:5180/admin

**Context:** Manual integration testing to verify the full flow works.

**Test steps:**
1. Start Docker: `make compose-up`
2. Navigate to http://localhost:5180/admin
3. See login form
4. Set token in .env if needed: `echo "ARES_OPERATOR_TOKEN=test-operator-secret" >> .env`
5. Restart Docker if token changed
6. Log in with token
7. Verify full state loads (sidebar + campaign data visible)
8. Test Campaign page: view, click Edit, change a field, save, verify update
9. Test Objectives page: view table, click Edit on a row, modal opens, edit, save, verify table updates
10. Test Clocks, Secrets, NPCs pages similarly
11. Test token persistence: reload page, verify still logged in
12. Test logout: click Logout, verify redirect to login form, verify localStorage cleared
13. Check browser console for no errors

---

## Task 14: Create Playwright screenshots

**Context:** Document the admin UI for the PR and future reference.

**Files:**
- Create: `assets/samples/ui-iteration/2026-05-06-C2-operator-app-desktop.png`
- Create: `assets/samples/ui-iteration/2026-05-06-C2-operator-app-mobile.png`

**Steps:**
1. Navigate to http://localhost:5180/admin, log in
2. Go to Objectives page (or any page)
3. Take screenshot at 1366×1024 (desktop)
4. Take screenshot at 390×844 (mobile)
5. Save both to assets/samples/ui-iteration/

---

## Success Criteria

- [ ] All 14 tasks complete
- [ ] `npm run build` passes (no TS/lint errors)
- [ ] `make check` passes
- [ ] Login flow works (token required, persist on reload, clear on logout)
- [ ] All 5 entity pages (Campaign, Objectives, Clocks, Secrets, NPCs) display tables
- [ ] Edit/modal flow works for all entities
- [ ] Patches refetch full state and update tables
- [ ] Error handling works (network failures, invalid token, etc.)
- [ ] Playwright screenshots captured
- [ ] Branch is clean and ready for PR

