# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A realistic 3D model of the owner's home (ground floor), built in Blender by Python scripts from a
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

Headless Blender 5.1 (the only supported way to run build scripts; Cycles uses 2x RTX 4090 via
OptiX):

```bash
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python <script.py> -- <args>
```

A Python exception can still exit 0 — print an `OK` sentinel and grep the log for `Traceback`.

Tests for the reusable snippets shipped with the skills:

```bash
# one Blender-side test (same pattern for test_bake.py, test_pbr.py, test_render.py)
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python .claude/skills/blender-arch-modelling/test_arch.py
# plan <-> 3D mapping maths for the viewer minimap
node .claude/skills/threejs-walkthrough-viewer/plan.test.mjs
# house spec consistency (once spec/validate_house.py exists)
python spec/validate_house.py
```

Extract a full-resolution reference still (frame N of `reference/frames` is at t = N-1 s):

```bash
ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/PXL_20261118_173753601.mp4" -frames:v 1 -q:v 2 reference/work/out.jpg
```

Deploy: GitHub Pages serves the `docs/` folder of `main` (legacy branch build, no Actions).
Committing and pushing `docs/` is the deploy.

## Architecture

The pipeline is one-directional; each stage consumes the previous stage's files:

1. `reference/` (private) → analysed into `spec/` — `layout.md`, `rooms/*.md`, reconciled into
   `spec/house.json`.
2. `blender/` — Python build scripts run headless: shared library (shell from `house.json`,
   moulding profile sweeps, joinery, PBR materials), one module per room for fittings and
   furniture, then lighting, lightmap bake and GLB export. Intermediate output (`.blend`, previews)
   goes to git-ignored `build/`.
3. `docs/` — the static site: three.js viewer, exported GLB + baked lightmaps, and the 2D plan
   drawn from the same `house.json` data so the position/heading marker always agrees with the 3D
   scene.

Constraints that shape the code:

- glTF export only carries image-textured Principled materials — procedural shader nodes do not
  survive, so every material must be baked to or authored as image textures.
- Realism in the browser comes from Cycles lighting baked to a second UV channel (`Lightmap`) and
  applied as `lightMap` in three.js, not from real-time lights.
- Verify visually: render low-res previews from eye-height cameras and compare against the
  reference frames listed in each `spec/rooms/<id>.md`; asserts alone miss inverted normals and
  misplaced openings.

## Project skills

`.claude/skills/` contains tested, Blender-5.1-specific guidance and helper modules — use them
rather than older snippets from memory (several 4.x APIs are gone in 5.x): `blender-headless-bpy`
(read first), `blender-arch-modelling`, `blender-pbr-gltf`, `blender-bake-lightmaps`,
`blender-interior-render`, `threejs-walkthrough-viewer`.
