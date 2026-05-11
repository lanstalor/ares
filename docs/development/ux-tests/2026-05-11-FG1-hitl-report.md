# FG1 HITL Playtest Report

**Date:** 2026-05-11
**Branch:** `focus-group/new-protagonist-intro`
**Evaluator:** Agent simulation via Playwright script
**Scenario:** FG1 Intro Scenario + First Meaningful Turn

## Summary
The Playwright simulation confirmed that the FG1 Intro Scenario and the first meaningful turn are functioning as expected without any blockers or hidden-state leakage. The UI properly guides the user and establishes the correct narrative context.

## Observations

- **Could you easily tell you are Mara, a Red, and a surface relay technician?**
  Yes. The intro sequence explicitly states: "Mara of Cimmeria is a highRed relay technician recruited by the Sons." The main UI participant strip correctly identifies the character as "Mara of Cimmeria" with the class "Guerrilla Technician".

- **Could you explain Relay 19 in one sentence based on the context?**
  Yes. It is a Ganymede surface relay tower where an urgent Weaver ghost packet must be intercepted before the Board of Quality Control or a Copper scrub detects it.

- **Did the ghost-packet timer create clear urgency?**
  Yes. The intro text ("pull a ghost packet from Relay 19 before a Copper scrub erases it or exposes it") clearly establishes a time-sensitive objective.

- **Did Gray surveillance read as immediate pressure?**
  Yes. In the very first turn response, the GM narrates: "One of the Gray supervisors at the checkpoint blister lifts a slate and points once toward the tower’s aft spine, where the diagnostic feed is already crawling." This directly introduces surveillance pressure.

- **Did you know what the command input expected?**
  Yes. The input area is clearly marked with `ares>` and an "EXECUTE" button, situated directly below a list of context-aware suggested actions.

- **Were the suggested actions useful or generic?**
  The suggested actions were highly specific and useful for the opening scene: `RUN COLD PULL`, `LOOP SUIT CAM`, `ASK ORAN`, and `FAKE COUPLING REPORT`.

- **Did the intro feel like it belongs to the playable scene?**
  Yes. The terminal boot sequence ("PROJECT ARES BOOT", "Establishing the Ganymede command shell") seamlessly transitions into the live narrative shell, providing a cohesive aesthetic experience.

## Exit Criteria Checklist
- [x] At least one human/agent completed the intro scenario.
- [x] The player can state protagonist, location, urgent objective, and first action.
- [x] Any severity-1 hidden-state leak, broken route, or first-turn blocker is fixed. (None observed).
- [x] Ready to merge FG3.