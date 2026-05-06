# Scene Art Registry

Reuse scene art before generating new environment images.

## Source of truth

- Frontend/library registry: `frontend/src/lib/sceneArtLibrary.js`
- Generation backlog: `data/assets/scene_generation_backlog.json`
- Matching CLI: `scripts/scene-art-registry.mjs`

## Workflow

1. Before generating a new scene, run:

```bash
node scripts/scene-art-registry.mjs match --query "spaceship hangar"
```

2. If the best match is already good enough, reuse that asset.
3. If the best match is only partial or there is no match, check:

```bash
node scripts/scene-art-registry.mjs backlog
```

4. Generate only the scenes still marked `missing` or `partial`.
5. After adding a new scene image:
   - copy or place it in `frontend/public/scene-art/`
   - add/update the entry in `frontend/src/lib/sceneArtLibrary.js`
   - update `data/assets/scene_generation_backlog.json` status and preferred asset

## Current gaps

The backlog currently calls out these missing or weakly-covered scenes:

- `Mars Wasteland`
- `Maintenance Deck`
- `Crescent Block Barracks`
- `The Melt`
- `The Gyre`
- `The Codovan Tier`
- `Lykos Station`
- `Copper Admin Hub`
- `Surface Relay Tower`
