# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A realistic 3D model of the owner's home — basement, ground, split-level first floor, loft, roof,
facades, garden, shed, side passage and forecourt — built in Blender by Python scripts from phone
walkthrough videos, and published as an interactive three.js viewer with linked 2D plan sheets at
https://timothywong731.github.io/home-design/.

**Read `spec/BRIEF.md` before any work**, then `blender/CONTRACT.md`, `blender/INTERACT.md` and
`blender/MULTILEVEL.md` (the binding multi-level / exterior contract; it wins over CONTRACT.md).

## Hard rules

- **The published site is public; the repo and `reference/` are private.** `reference/` (video
  frames, audio, transcript) is git-ignored and must stay that way. Never model or publish the
  street name on the front-door transom, house numbers, number plates, faces/photos of people,
  whiteboard writing, fridge magnets or documents. The only reference-derived pixels allowed in
  tracked files are rectified crops of paintings/tapestry/rug patterns (no people) under
  `blender/textures/art/`.
- **Coordinates:** metres, Z up. Origin = centre of the inside face of the front-door threshold at
  vestibule floor level (ground-floor FFL = 0; every other floor and the site carry world Z). +Y runs
  from the front door into the house, +X is to the right walking in. In three.js this becomes
  (x, z, -y) — see `threeToPlan`/`planToThree` in the viewer skill.
- **`spec/house.json` (schema `house/2`) is the single source of truth** for levels (`B G 1 2`, plus
  `X` = everything outside), rooms, walls, openings, stairs, roof and the `exterior` (zones,
  boundaries, shed, facades). The shell, site, envelope, plan sheets and the walk layers are all
  generated from it — change geometry there, not downstream. Per-room detail: `spec/rooms/<id>.md`.
- **Never drive the live Blender MCP (`mcp__blender__*`) from subagents or parallel work** — it is
  one shared GUI instance. All builds run headless. Pass absolute render paths (a relative one lands
  on the drive root).
- Declutter: model architecture, joinery, cabinetry, appliances, real furniture, art, lighting and
  a few permanent ornaments; omit bags, clothes, pet items and countertop mess.

## Commands

Headless Blender 5.1 is the only supported way to run build scripts (Cycles uses 2x RTX 4090 via
OptiX). A Python exception can still exit 0, so every script prints a sentinel: grep the log for
it and for `Traceback`. Full re-run, in this order (each stage reads the previous stage's files):

```bash
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
python spec/validate_house.py            # after editing spec/house.json; redraws spec/plan_<level|site|section>.png
# 1. build everything -> build/home.blend          (BUILD OK, ~1 min; triangle budgets by level / room / kind)
"$B" -b --factory-startup --python blender/build.py -- --save build/home.blend
#    foundation only (6 s): --only shell,site,envelope      one room: --only shell,living --preview living --res 540x960 --samples 64 --tag me
#    --levels B,G,1,2,X     --preview <room>|level:<id>|plan:<level>|section|elev:front|rear|flank     --pose 1 (everything operated)
# 2. export -> docs/assets: glb/<level>.glb, lightmaps, probes, sky.jpg, manifest (schema 2), footprints, hero stills   (EXPORT OK)
"$B" -b --factory-startup build/home.blend --python blender/export.py -- --out docs/assets --samples 1024 --renders
#    --bake-res N (upper bound of the atlas side, default 4096)   --skip-bake (GLBs + manifest + footprints, 30 s)
#    --rooms a,b [--levels L] (re-bake a subset)   --stills-only [--still-res 960x540]
#    dry run, never into docs/ (8 min): --out build/export_int --tmp build/export_int_tmp --bake-res 1024 --samples 128
python blender/export_fixture.py --check docs/assets                                             # EXPORT CHECK OK (manifest vs files)
"$B" -b --factory-startup --python blender/export_check.py -- --assets docs/assets --level G   # CHECK OK; re-lit views in <tmp>/check
# 3. plan sheets B G 1 2 + site from spec/house.json + footprints.json -> plan.json, house-plans.dxf / .pdf, then audit
python tools/plan/draft.py && python tools/plan/check.py && python tools/plan/test_draft.py    # PLAN OK / CHECK OK / TEST OK; rasters in build/plan/
#    on a dry-run export: draft.py --footprints build/export_int/footprints.json --out build/export_int; check.py --assets build/export_int
# 4. viewer tests (one-time: npm install --prefix build/e2e playwright@1.65.1)
node docs/test/geom.test.mjs                                    # walk layers, portals, the seven route traces of MULTILEVEL.md 16
node docs/test/e2e.mjs [--assets build/export_int] [--only desktop,ref,realtime,phone,ix,levels]   # ALL CHECKS PASSED; screenshots in build/e2e/levels/
```

What to re-run: `spec/house.json` or `blender/lib` changed → all four; a room module → 1,
2 (`--rooms <room> --levels <its level>`), 3 (footprints may have moved), 4; `tools/plan` → 3, 4;
`docs/js` → 4. Read the previews, re-lit views, plan rasters, stills and screenshots after each
run; the asserts do not judge how it looks.

Library checks (one sentinel each): `python blender/test_ctx.py` (CTX OK) and
`"$B" -b --factory-startup --python blender/test_shell.py [-- --sky]` (SHELL OK), `test_site.py`
(SITE OK), `test_envelope.py` (ENVELOPE OK), `test_joinery.py` (JOINERY OK). Skill snippet tests:
`"$B" -b --factory-startup --python .claude/skills/blender-arch-modelling/test_arch.py` (same
pattern for `test_bake.py`, `test_pbr.py`, `test_render.py`) and
`node .claude/skills/threejs-walkthrough-viewer/plan.test.mjs`.

Extract a full-resolution reference still (frame N of a video's `frames/` is at t = N-1 s; file
names per video are in `spec/BRIEF.md`):

```bash
ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/PXL_20261118_173753601.mp4" -frames:v 1 -q:v 2 reference/work/out.jpg
```

Deploy: GitHub Pages serves the `docs/` folder of `main` (legacy branch build, no Actions).
Committing and pushing `docs/` is the deploy; the first schema-2 export into `docs/assets` deletes
`home.glb`, so viewer and assets land in the same commit. Budgets (asserted by `export.py`):
triangles 4.0 M in all (G 0.85 M, 1 1.3 M, 2 0.85 M, B 0.15 M, X 0.85 M); every GLB ≤ 40 MB and
`glb/G.glb` ≤ 21.5 MB; first view (`glb/G.glb` + level-G lightmaps and probes + json) < 35 MB;
`docs/` < 300 MB; no file over 50 MB. `ATLAS_CAP` in `export.py` trims a room when one fails.

## Architecture

The pipeline is one-directional; each stage consumes the previous stage's files:

1. `reference/` (private) → analysed into `spec/` — `layout*.md`, `rooms/*.md`, `phase2/*.md`,
   reconciled into `spec/house.json`.
2. `blender/build.py` → `build/home.blend`, in stages: `shell` (`lib/shell.py`: the envelope blocks
   filled as mass and rooms carved out, flight carcasses, then joinery and trim), `site`
   (`lib/site.py`: ground zones, steps, boundaries, gate, shed), `envelope` (`lib/envelope.py`:
   facade skin, exterior reveals, roof, roof windows, balcony), then one `rooms/<module>.py` per
   room or pseudo-room. Objects carry custom props (`room`, `level`, `kind`, `lm` = static |
   dynamic, `plan_sym`, `ix`) that drive everything downstream; `level` is always the level of the
   object's room (`front side_passage garden shed facade roof neighbours` are level `X`). API:
   `blender/lib/README.md`.
3. `blender/export.py` (+ `export_bake.py`) → `docs/assets/`: one GLB per level (flat node list,
   meshopt + WebP), one Cycles lightmap atlas per room for `lm='static'` objects (second UV set),
   an equirect probe per room for everything else, a lights-off set, `sky.jpg`, `manifest.json`
   (schema 2: levels, load order, rooms, lightmaps, probes, white balance, sky, viewpoints, first
   view), `footprints.json` (plan symbols = walk obstacles) and the hero stills in `docs/renders/`.
4. `tools/plan/draft.py` → `plan.json` (five sheets in one world frame, drawn by
   `docs/js/plan2d.js`), DXF and PDF from one entity list, so the on-screen plan, the downloads and
   the 3D model stay in registration.
5. `docs/` — static three.js viewer, no build step: `js/main.js` (levels stream in by
   `loadOrder`, baked lighting, walk and dollhouse modes with a cut per level, UI), `js/geom.js`
   (pure frame mapping, walk layers B / G / 1 / 2 + one per flight, portals, routing; node-tested),
   `js/interact.js` (operable things from `ix` tags, started per level as each GLB arrives),
   `js/plan2d.js` (CAD canvas with sheet tabs, position marker and view cone).

Constraints that shape the code:

- glTF export only carries image-textured Principled materials — procedural shader nodes do not
  survive, so every material must be baked to or authored as image textures.
- Realism in the browser comes from Cycles lighting baked to a second UV channel (`Lightmap`) and
  applied as `lightMap` in three.js, not from real-time lights. One white balance (3000 K) for
  everything, indoors and outdoors: it is multiplied into lightmaps and probes at export and applied
  to emissive colours in the viewer. The sky that lights the scene is therefore lamp-coloured; the
  camera (previews, probes, `sky.jpg`) sees a separate display sky (`lighting.setup_sky`).
- glTF-Transform runs only `resize`, `webp`, `meshopt`: `prune` / `dedup` / `join` drop the
  lightmap UVs, node names or extras the viewer relies on. Node names are unique across all level
  GLBs; an interaction group never spans two levels.
- Verify visually: render low-res previews from eye-height cameras and compare against the
  reference frames listed in each `spec/rooms/<id>.md`; asserts alone miss inverted normals and
  misplaced openings.

## Project skills

`.claude/skills/` contains tested, Blender-5.1-specific guidance and helper modules — use them
rather than older snippets from memory (several 4.x APIs are gone in 5.x): `blender-headless-bpy`
(read first), `blender-arch-modelling`, `blender-pbr-gltf`, `blender-bake-lightmaps`,
`blender-interior-render`, `threejs-walkthrough-viewer`.
