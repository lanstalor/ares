# PROJECT ARES

## Canonical Build Spec and Agent Operations Guide

### Self-Hosted AI TTRPG Platform for a Red Rising Fan Campaign

---

## What This Document Is

This repository does not contain the application yet. Right now it contains the planning documents that define it:

- `world_bible.md` - the campaign source material
- `readme.md` - this build and operations spec

This README is the canonical execution document for Project Ares v1. It defines:

- the product shape
- the architecture
- the domain model
- the live play loop
- the operator workflows
- the Codex CLI agent playbooks used to build and maintain the system

It is intentionally written as a target spec, not as a description of code that already exists.

---

## Product Definition

Project Ares is a self-hosted AI TTRPG platform for a pre-Darrow Red Rising fan campaign set in 728-732 PCE. The campaign follows a Sons of Ares cell operating on Ganymede.

The core product is not "chat with an LLM about a setting." The core product is:

- a hidden-state AI Game Master
- a structured campaign world seeded from `world_bible.md`
- a live play loop that preserves mystery, secrecy, and canon
- a CLI-first operator workflow for setup, review, repair, and editorial QA

The player should be able to play inside the world without seeing how the world is being managed behind the curtain.

### V1 Shape

Version 1 is explicitly:

- single-player
- one human player
- one AI GM during live play
- browser-based for play
- CLI-first for setup and maintenance
- field-level visibility aware
- provider-abstracted from day one
- strong hidden-state autonomous on the backend

Version 1 is not:

- a broad multiplayer platform
- a human-first world editor
- a map-heavy UI product
- an asset browser
- a generic chatbot app

---

## Design Principles

### 1. Hidden State Is The Product

The backend must know more than the player knows. It must preserve secrets, unresolved threads, reveal timing, and NPC intent without leaking that structure directly into the player experience.

### 2. Canon Beats Convenience

If the system has to choose between a fast answer and a canon-faithful answer, it chooses canon.

### 3. Suspense Beats Transparency

The player should not see the full quest tree, mystery solution, or secret state just because the system has it.

### 4. Structured State Beats Prompt Soup

Prompting matters, but the system cannot rely on prompt text alone. Secrets, reveals, clocks, and long-lived facts must exist as structured backend state.

### 5. CLI-First Operations

Outside live play, the operator experience is built around agentic CLI workflows, not around a broad CRUD dashboard.

### 6. Advisory Agents Stay Advisory

Story, style, UX, and research agents can critique and recommend. They do not become canon automatically.

---

## Source Of Truth

`world_bible.md` is the seed source for world import.

After import:

- the database becomes the source of truth for runtime state
- structured hidden state lives in the backend
- edits happen through controlled operator workflows
- `world_bible.md` remains a seed artifact, not the primary runtime editor

This is necessary because live play creates state the markdown file does not contain:

- discovered facts
- locked and unlocked entries
- hidden clocks
- NPC agendas
- revised memory records
- campaign-specific consequences

---

## V1 User Experience

### Player Surface

The first live-play interface is a minimal web app. It should feel like an old DOS text RPG with restrained pixel-art chrome.

The UI direction for v1:

- text-first
- low-friction
- readable over long sessions
- retro terminal mood without fake gimmicks
- pixel-art framing and UI elements where useful
- future-friendly for character, item, and world pixel assets

The UI should not depend on final art to be usable.

### Operator Surface

Operators use CLI-first workflows, ideally driven by Codex CLI plus other coding agents where useful.

The operator workflows should support:

- initial bible import
- import validation
- session prep
- continuity review
- style review
- state audit
- post-session repair
- selective canon corrections

The web app is for play. The CLI is for maintenance and editorial control.

---

## Technical Direction

### Recommended Stack

The target stack for v1 is:

```text
Backend:   Python + FastAPI
Database:  PostgreSQL + pgvector
Frontend:  React web app
AI:        Provider abstraction over generation and embeddings
Hosting:   Self-hosted via Docker Compose on Unraid or equivalent
Auth:      Minimal local auth/session model
```

### Why This Stack

- FastAPI is a good fit for a stateful orchestration backend
- PostgreSQL can hold both structured campaign state and vector-backed memory search
- pgvector removes the need for a separate memory service in v1
- React is sufficient for a text-first web client with a controlled visual style
- Docker Compose is the simplest deployment model for self-hosted iteration

### Provider Abstraction

Provider abstraction is required from day one, but v1 should still implement a concrete first path.

The architecture must separate:

- text generation
- embeddings
- optional utility-model work such as extraction or validation

Do not build a giant plugin system up front. Build clear adapter boundaries with one concrete implementation path first.

---

## Target Architecture

This is the intended system shape, not a description of files already present.

### 1. Content Ingestion Layer

Responsibilities:

- parse `world_bible.md`
- extract entities and relationships
- infer visibility metadata
- seed structured campaign data
- seed hidden facts and revealable information

Outputs:

- normalized world entities
- seeded secrets and reveal conditions
- initial campaign-opening data

### 2. Narrative State Layer

Responsibilities:

- store visible and hidden campaign state
- track discovered vs undiscovered information
- store active objectives, memories, and clocks
- enforce field-level visibility rules

This layer holds the durable truth of the campaign.

### 3. GM Orchestration Layer

Responsibilities:

- assemble player-safe and hidden context
- select relevant memories and world facts
- advance hidden clocks and NPC agendas
- decide reveal eligibility
- call the generation provider
- parse consequences out of model output
- update state while preserving secrecy

This layer is the AI GM in practice. It is not a thin prompt wrapper.

### 4. Canon Guard Layer

Responsibilities:

- detect forbidden characters or impossible technologies
- detect contradictions with fixed canon points
- flag or block responses that drift
- support post-session repair workflows

### 5. Operator Workflow Layer

Responsibilities:

- run import and audit flows
- support continuity and style review
- support state inspection and repair
- enable narrow approved canon maintenance

### 6. Live Play Web Layer

Responsibilities:

- turn feed
- player input
- current location and state panel
- minimal retro presentation
- no hidden-state leakage

---

## Core Domain Model

The implementation should treat these as first-class concepts.

### World Entities

- `Area`
- `POI`
- `Faction`
- `NPC`
- `LorePage`

### Campaign Entities

- `Campaign`
- `Character`
- `Objective` or `Quest`
- `Turn`
- `Memory`
- `Clock`
- `Secret` or `RevealableFact`

### Control Entities

- `VisibilityPolicy`
- `AgentRun` or equivalent audit record
- `CanonIssue`
- `StatePatch` or equivalent repair record

### Visibility Model

Visibility must be field-level, not only record-level.

Expected visibility states:

- `player_facing`
- `gm_only`
- `sealed`
- `locked`

Interpretation:

- `player_facing`: safe to show to the player
- `gm_only`: visible to the orchestration system and operator workflows, never directly surfaced to the player
- `sealed`: hidden truth that may drive live play but should remain concealed until explicitly revealed
- `locked`: discoverable, but not yet available to the player

Example:

- an NPC appearance may become `player_facing`
- their location may remain `locked`
- their hidden agenda may be `sealed`
- a GM note about reveal timing may be `gm_only`

---

## Hidden State Requirements

The backend must maintain structured hidden state for at least:

- unresolved secrets
- NPC goals and current knowledge
- reveal conditions
- plot clocks and pressure clocks
- mission consequences not yet visible to the player
- canon-sensitive facts
- operator annotations

The player must never receive this structure directly through:

- UI rendering
- API responses meant for the player
- AI narration
- memory summaries

The only path from hidden state to player knowledge is an intentional in-world reveal.

---

## Live Turn Loop

The live turn loop is the core runtime behavior.

### Input

The system accepts:

- campaign identifier
- character identifier
- player input text

### Runtime Flow

For each turn, the backend should:

1. load current visible and hidden campaign state
2. resolve current location, active objective, and nearby actors
3. retrieve recent turns and relevant long-term memories
4. retrieve hidden secrets, clocks, agendas, and reveal candidates relevant to the scene
5. assemble a player-safe narration brief plus hidden GM context
6. call the GM model
7. extract structured consequences from the response
8. run canon and leakage checks
9. update campaign state, clocks, memory, and reveal status
10. store an auditable turn record
11. return only player-safe output

### Required Output

The player-facing response may include:

- narration
- explicit visible consequences
- updated visible character state
- updated visible location or objective state

The player-facing response must not include:

- hidden clocks
- unrevealed causes
- sealed notes
- internal prompt material
- continuity diagnostics

---

## Canon Rules

The world bible is not flavor text. It is a source document for system constraints.

### Fixed Rules

The implementation must enforce:

- campaign window: 728-732 PCE
- Ganymede-centered campaign frame
- no Darrow, Eo, Cassius, Virginia, or Mustang in live play
- no AI
- no FTL
- no magic
- Red Rising speech and social hierarchy rules
- fixed canon events remain fixed

### Tone Rules

The narration system must preserve:

- grimdark political thriller tone
- moral ambiguity
- tension through surveillance, pressure, and consequence
- lowColor vulnerability inside a violently stratified system

### Failure Policy

If output drifts from canon, the system must:

- block it
- repair it
- or flag it for operator review

It must not silently accept canon drift as normal.

---

## Agentic Operations Model

Project Ares should explicitly use agentic workflows during development and maintenance.

There are two distinct AI roles in this project:

- the live-play backend GM, which runs during the game
- operator agents, which help build, test, validate, and critique the system outside live play

These roles must remain separate.

### Operator Agent Rules

- research agents are human-in-the-loop
- creative and editorial agents are advisory only
- continuity agents may perform narrow mechanical fixes and minor prose corrections only
- no agent may silently rewrite core canon, mystery solutions, reveal truths, or character intent
- canon-significant changes require explicit human approval

### Output Standard

Every named playbook should return some combination of:

- objective
- inputs reviewed
- findings
- severity or confidence
- recommended actions
- whether any mutation was proposed or applied

Technical and validation workflows should use structured scorecards.

Creative workflows should use prose critique, optionally paired with structured findings.

---

## Named Agent Playbooks

These are first-class workflows the system should support.

### 1. UI/UX Test Agent

Mission:

- evaluate the live-play interface for clarity, readability, retro feel, and sustained usability

Inputs:

- running UI
- screenshots
- key interaction flows

Outputs:

- structured findings
- severity-ranked UX issues
- prose critique on atmosphere and usability

Guardrails:

- advisory only
- does not rewrite product scope

Primary checks:

- text readability over long sessions
- clarity of state and action affordances
- retro DOS feel without gimmick overload
- mobile degradation behavior
- hidden-state safety in the interface

### 2. Story Editor / Critique Agent

Mission:

- critique scenes, objectives, reveals, and mystery structure

Inputs:

- quest drafts
- scene summaries
- generated session logs
- operator notes

Outputs:

- prose critique
- findings on pacing, stakes, reveal timing, and payoff

Guardrails:

- advisory only
- cannot make canon-significant edits automatically

Primary checks:

- suspense quality
- twist quality
- emotional payoff
- clarity of stakes
- whether the mystery is fair but not obvious

### 3. Style Editor Agent

Mission:

- enforce narration voice and Red Rising tonal discipline

Inputs:

- generated narration
- prompt templates
- story drafts

Outputs:

- prose critique
- targeted style corrections
- flags for generic prose or tonal drift

Guardrails:

- advisory only
- cannot become canon automatically

Primary checks:

- speech register consistency
- grimdark tone
- diction quality
- avoidance of generic fantasy or modern-chatbot phrasing

### 4. World / Character Continuity Agent

Mission:

- validate continuity across world state, characters, timelines, and reveal order

Inputs:

- seeded world data
- campaign state
- session logs
- secrets and reveal structures

Outputs:

- structured report
- contradiction list
- proposed narrow corrections

Guardrails:

- may apply mechanical fixes
- may apply minor prose corrections that do not alter meaning
- may not change plot facts, mystery answers, character intent, or core canon without approval

Primary checks:

- chronology
- identity consistency
- faction consistency
- visibility consistency
- reveal order
- unresolved contradiction tracking

### 5. Web Research Agent

Mission:

- gather external information for tech, UI, pricing, implementation references, or comparable products

Inputs:

- research question
- target decision
- source constraints

Outputs:

- sourced summary
- recommendation
- explicit uncertainty notes

Guardrails:

- human-in-the-loop
- cannot change canon
- cannot silently change architecture or spending decisions

Primary checks:

- source quality
- recency
- relevance
- implementation impact

### 6. Prompt / GM Behavior Agent

Mission:

- inspect prompt design, hidden-state handling, retrieval discipline, and leakage risk

Inputs:

- prompts
- assembled contexts
- generated turns

Outputs:

- structured findings
- recommendations for prompt and retrieval improvements

Guardrails:

- advisory only

Primary checks:

- hidden-state leakage risk
- prompt bloat
- retrieval quality
- canon compliance
- state extraction reliability

### 7. State Audit Agent

Mission:

- inspect live campaign state after play and identify broken data, leaked knowledge, invalid clocks, or malformed memory

Inputs:

- database state
- session log
- audit snapshots

Outputs:

- structured report
- repair recommendations
- optional narrow state patch proposal

Guardrails:

- may propose repair patches
- auto-applied repair should be limited to clearly mechanical fixes

Primary checks:

- bad visibility flags
- leaked hidden facts
- impossible world state
- malformed memory data
- orphaned references

### 8. Seed / Import Validation Agent

Mission:

- compare imported data against `world_bible.md`

Inputs:

- seed document
- imported entities
- extraction logs

Outputs:

- gap report
- malformed extraction report
- recommendations for import repair

Guardrails:

- advisory by default
- can assist with narrow data repair workflows

Primary checks:

- missing entities
- bad relationships
- wrong visibility extraction
- broken chronology links
- missing campaign-opening content

### 9. Additional Agent Types To Add Later

The design should remain friendly to additional workflows such as:

- playtest simulation agent
- economy and inventory balance agent
- accessibility reviewer
- session recap editor
- canon drift sentinel
- quest design critic
- security and privacy reviewer for hidden-state boundaries

---

## Target CLI Workflows

These workflows should exist even if the exact commands are defined later.

### Import Workflow

Purpose:

- seed the database from `world_bible.md`
- extract entities, relationships, visibility, secrets, and opening state

### Validation Workflow

Purpose:

- compare seeded state to source material
- catch missing or malformed imports

### Session Prep Workflow

Purpose:

- inspect current campaign state
- review clocks and hidden agendas
- verify canon-sensitive conditions
- prepare the next play session

### Post-Session Review Workflow

Purpose:

- audit generated memories
- check for canon drift
- identify bad reveals or leakage
- lock or repair correct records

### Continuity Review Workflow

Purpose:

- inspect world, character, and timeline consistency
- propose narrow repairs

### Style Review Workflow

Purpose:

- critique generated narration and prompt behavior
- enforce tonal discipline

### Research Workflow

Purpose:

- gather sourced external information for technical or design decisions

---

## Implementation Phases

This is the recommended build order.

### Phase 0 - Project Foundation

Deliverables:

- repository scaffolding
- backend and frontend skeletons
- database setup
- provider interface boundaries
- deployment baseline

Success criteria:

- app boots locally
- database connects
- provider adapters have defined interfaces

### Phase 1 - Seed And Domain Core

Deliverables:

- import pipeline for `world_bible.md`
- normalized world entities
- campaign and character models
- visibility model
- secrets and clocks

Success criteria:

- the bible seeds structured data successfully
- visibility states exist at field level
- opening campaign state is representable

### Phase 2 - GM Engine

Deliverables:

- context assembly
- memory retrieval
- hidden-state retrieval
- canon guard
- consequence extraction
- state update pipeline

Success criteria:

- one complete turn runs end-to-end
- hidden state is used without leaking
- invalid output is blocked or flagged

### Phase 3 - Operator Agent Workflows

Deliverables:

- seed validation workflow
- continuity workflow
- style workflow
- state audit workflow
- session prep and review workflows

Success criteria:

- workflows produce useful reports
- narrow mechanical repairs are possible
- canon-significant edits still require approval

### Phase 4 - Live Play Web UI

Deliverables:

- text-first browser client
- turn feed
- input composer
- current state panel
- retro visual direction

Success criteria:

- the player can play the opening scene in browser
- the UI is readable and stable over long-form text
- hidden-state data does not leak through the client

### Phase 5 - Deferred Expansion

Deferred until the core loop is stable:

- multiplayer
- human-first admin dashboard
- map-heavy exploration UI
- broad world editing UX
- rich asset galleries
- expanded campaign authoring tools

---

## Acceptance Criteria

The system is not "working" until these cases pass.

### Import Test

`world_bible.md` seeds:

- world entities
- visibility metadata
- secrets
- revealable facts
- clocks
- opening campaign state

### Visibility Test

A `sealed` or `locked` field:

- is accessible to the GM engine
- is not exposed in player output
- is not exposed through the player API or UI

### Turn Loop Test

The campaign opening can run end-to-end:

- input accepted
- context assembled
- narration generated
- state updated
- turn and memory stored

### Hidden-State Test

The system can:

- advance a hidden clock
- change an NPC agenda
- preserve that change without surfacing the underlying mechanic directly

### Canon Guard Test

Generated content containing forbidden characters, impossible technology, or canon contradictions is:

- blocked
- corrected
- or flagged for review

### Agent Workflow Test

A named operator workflow can:

- inspect inputs
- produce findings
- return a consistent report shape

### Continuity Mutation Test

The continuity workflow can apply:

- a mechanical correction
- or a minor prose correction

without altering:

- plot meaning
- mystery answers
- core canon truth

### UI Test

The web client supports:

- long-form readable play
- retro text-RPG presentation
- stable interaction without final art assets

### Research Test

A research workflow can:

- gather external sources
- summarize them
- produce recommendations

without automatically changing canon or architecture

---

## Non-Goals For V1

These are explicitly not first-priority goals:

- broad multiplayer support
- a general-purpose TTRPG engine
- a human-first CMS for campaign authoring
- real-time co-op play
- full art pipeline integration
- exhaustive UI polish before the hidden-state GM loop works

---

## Summary

Project Ares is a hidden-state AI GM system, not just a lore-aware chatbot. The value of the platform comes from maintaining structured world truth, preserving secrecy, enforcing canon, and allowing a human player to experience surprise inside a controlled narrative machine.

The build order should prioritize:

- seed and state correctness
- visibility and secrecy correctness
- GM orchestration correctness
- operator review workflows
- then the player-facing web experience

If the system cannot preserve hidden truth and suspense, it has failed even if the UI looks good.

---

*Project Ares*
*The Society believes it has perfected humanity. Ares believes it has only perfected its chains.*
