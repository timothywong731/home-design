# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A realistic 3D model of the owner's home, built in Blender by Python scripts from a
phone walkthrough video, and published as an interactive three.js viewer with a linked 2D floor
plan at https://timothywong731.github.io/home-design/.

**Read `spec/BRIEF.md` before any work.** It holds the owner's requirements (including spoken
priorities transcribed from the video), the frame-number conventions for the reference footage,
and the rules below in full.

## Hard rules

- **The published site is public; the repo and `reference/` are private.** `reference/` (video
  frames, audio, transcript) is git-ignored and must stay that way. Never model or publish the
  street name on the front-door transom, faces/photos of people, whiteboard writing, fridge
  magnets or documents. The only reference-derived pixels allowed in tracked files are rectified
  crops of paintings/tapestry/rug patterns (no people) under `blender/textures/art/`.
- **Coordinates:** metres, Z up. Origin = centre of the inside face of the front-door threshold at
  vestibule floor level. +Y runs from the front door into the house, +X is to the right walking
  in. In three.js this becomes (x, z, -y) — see `threeToPlan`/`planToThree` in the viewer skill.
- **`spec/house.json` is the single source of truth** for rooms, walls, openings and levels. The
  Blender shell, the 2D floor plan and the 3D↔2D mapping are all generated from it — change
  geometry there, not in downstream code. Per-room visual detail lives in `spec/rooms/<id>.md`.
- **Never drive the live Blender MCP (`mcp__blender__*`) from subagents or parallel work** — it is
  one shared GUI instance. All builds run headless.
- Declutter: model architecture, joinery, cabinetry, appliances, real furniture, art, lighting and
  a few permanent ornaments; omit bags, clothes, pet items and countertop mess.

## Commands

Headless Blender 5.1 is the only supported way to run build scripts (Cycles uses 2x RTX 4090 via
OptiX). A Python exception can still exit 0, so every script prints a sentinel: grep the log for
it and for `Traceback`. Full re-run, in this order (each stage reads the previous stage's files):

```bash
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
python spec/validate_house.py                                   # after editing spec/house.json
# 1. build shell + all rooms -> build/home.blend            (BUILD OK, ~1 min; prints triangle budgets)
"$B" -b --factory-startup --python blender/build.py -- --save build/home.blend
#    one room while iterating: --only shell,living --preview living --res 540x960 --samples 64 --tag me
# 2. export to docs/: lightmaps, probes, home.glb, manifest, footprints, hero stills   (EXPORT OK, ~13 min)
"$B" -b --factory-startup build/home.blend --python blender/export.py -- --out docs/assets --bake-res 4096 --samples 1024 --renders
#    --skip-bake       GLB + manifest + footprints only, 15 s (valid while geometry is unchanged)
#    --rooms a,b       re-bake / re-render only these rooms
#    --stills-only [--still-res 960x540]    hero stills only (cameras: HEROES in blender/export.py)
# 3. CAD plan from spec/house.json + docs/assets/footprints.json -> plan.json, DXF, PDF, then audit
python tools/plan/draft.py && python tools/plan/check.py       # PLAN OK / CHECK OK, rasters in build/plan/
# 4. viewer tests (one-time: npm install --prefix build/e2e playwright@1.65.1)
node docs/test/geom.test.mjs                                    # frame mapping, walkable area, route into every room
node docs/test/e2e.mjs                                          # Chromium run, screenshots in build/e2e/
```

What to re-run: `spec/house.json` or `blender/lib` changed → all four; a room module → 1, 2, 3
(footprints may have moved), 4; `tools/plan` → 3, 4; `docs/js` → 4. Read the screenshots, plan
rasters and stills after each run; the asserts do not judge how it looks.

Tests for the snippets shipped with the skills: `"$B" -b --factory-startup --python
.claude/skills/blender-arch-modelling/test_arch.py` (same pattern for `test_bake.py`,
`test_pbr.py`, `test_render.py`) and `node .claude/skills/threejs-walkthrough-viewer/plan.test.mjs`.

Extract a full-resolution reference still (frame N of `reference/frames` is at t = N-1 s):

```bash
ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/PXL_20261118_173753601.mp4" -frames:v 1 -q:v 2 reference/work/out.jpg
```

Deploy: GitHub Pages serves the `docs/` folder of `main` (legacy branch build, no Actions).
Committing and pushing `docs/` is the deploy. Budgets: `home.glb` < 40 MB, lightmaps + probes
< 25 MB, `docs/` < 90 MB, no file over 50 MB.

## Architecture

The pipeline is one-directional; each stage consumes the previous stage's files:

1. `reference/` (private) → analysed into `spec/` — `layout.md`, `rooms/*.md`, reconciled into
   `spec/house.json`.
2. `blender/build.py` — `lib/` (shell from `house.json`, mouldings, joinery, materials, props,
   lighting) plus one `rooms/<id>.py` per room → `build/home.blend`. Objects carry custom props
   (`room`, `kind`, `lm` = static | dynamic, `plan_sym`) that drive everything downstream. API:
   `blender/lib/README.md`; rules: `blender/CONTRACT.md`.
3. `blender/export.py` (+ `export_bake.py`) → `docs/assets/`: `lm='static'` objects get a second
   UV set and one Cycles lightmap atlas per room; everything else is lit by its room's equirect
   probe. `home.glb` (flat node list, meshopt + WebP), `manifest.json` (lightmaps, probes, white
   balance, sky, room-jump viewpoints), `footprints.json` (plan symbols = walk obstacles) and the
   hero stills in `docs/renders/`.
4. `tools/plan/draft.py` → `plan.json` (drawn by `docs/js/plan2d.js`), DXF and PDF from one
   entity list, so the on-screen plan, the downloads and the 3D model stay in registration.
5. `docs/` — static three.js viewer, no build step: `js/main.js` (loading, baked lighting, walk
   and dollhouse modes, UI), `js/geom.js` (pure frame mapping and collision, node-tested),
   `js/plan2d.js` (CAD canvas with position marker and view cone).

Constraints that shape the code:

- glTF export only carries image-textured Principled materials — procedural shader nodes do not
  survive, so every material must be baked to or authored as image textures.
- Realism in the browser comes from Cycles lighting baked to a second UV channel (`Lightmap`) and
  applied as `lightMap` in three.js, not from real-time lights. Lamps are 3000 K: the white
  balance of the Cycles view is multiplied into lightmaps and probes at export and applied to
  emissive colours in the viewer.
- glTF-Transform runs only `resize`, `webp`, `meshopt`: `prune` / `dedup` / `join` drop the
  lightmap UVs, node names or extras the viewer relies on.
- Verify visually: render low-res previews from eye-height cameras and compare against the
  reference frames listed in each `spec/rooms/<id>.md`; asserts alone miss inverted normals and
  misplaced openings.

## Project skills

`.claude/skills/` contains tested, Blender-5.1-specific guidance and helper modules — use them
rather than older snippets from memory (several 4.x APIs are gone in 5.x): `blender-headless-bpy`
(read first), `blender-arch-modelling`, `blender-pbr-gltf`, `blender-bake-lightmaps`,
`blender-interior-render`, `threejs-walkthrough-viewer`.
