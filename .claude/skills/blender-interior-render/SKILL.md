---
name: blender-interior-render
description: Use when lighting and rendering realistic interior stills (or preparing the lighting that will be baked) in Blender Cycles by script - window portals, sun/sky, warm lamps, colour management (AgX/Filmic/Standard), exposure, eye-height cameras, denoising and render verification.
---

# Interior lighting and stills

Tested helpers in `render_setup.py` (`test_render.py` renders a windowed room in 5.1.1): `colour_management`, `world_sky`, `sun`, `window_portal`, `lamp`, `camera`, `cycles_still`.

## Recipe
1. **Colour management**: `view_transform='AgX'`, look `'Medium High Contrast'` for photographic previews. For *baking* and for judging true paint colour use `'Standard'` (what a web viewer without tone mapping shows). Compare albedo colours under Standard only. Exposure via `view_settings.exposure` (start 0; typical daylight interior needs -1 to +1 EV with sun 3-5).
2. **Daylight**: World Background = sky colour (or Nishita sky node) strength 1-2, plus a `SUN` (strength 2-5, angle 0.53 deg, 5500 K). Windows: leave glass out of the light path (or as a thin transparent/transmissive with *shadow ray* passes off in Cycles) and add an **area light with `light.cycles.is_portal=True`** just inside each opening, facing into the room, covering the opening. Portals add no energy, they only guide sampling (essential for rooms lit only through windows). Requires a non-black World.
3. **Artificial light**: warm bulbs 2700 K (`use_temperature`), point/spot power 40-100 W for table/ceiling lamps (Blender watts are radiometric - tune by exposure), radius 0.05-0.08 for soft shadows; chandelier = several small emissive bulbs; LED strips = emissive meshes. Warm LED/phone-video colour casts: match *lighting*, but keep *albedo* neutral.
4. **Cycles settings** (`cycles_still`): 256-1024 spp + OpenImageDenoise, `sample_clamp_indirect` ~10 against fireflies, bounces 8 total/4 diffuse, light tree on. GPU: OPTIX then CUDA, enable non-CPU devices explicitly (factory-startup resets prefs).
5. **Camera**: eye height 1.5-1.65 m, lens 16-20 mm (full frame 36 mm) for rooms, never tilt - keep verticals straight (use `shift_y` for headroom), clip_start 0.05. Place at room corners looking along the diagonal.
6. **Materials sanity**: no pure white (0.8 max) or pure black (0.03 min) albedo; add small roughness variation; glossy floors need roughness 0.25-0.5.
7. **Verification loop**: render 160x90 @ 16 samples CPU; Read the PNG; check mean brightness (not black/white), then raise quality. Compare against the reference frame at the same viewpoint.

## Gotchas
- 5.x: `BLENDER_EEVEE` for EEVEE; `scene.eevee.use_gtao` removed; EEVEE shadows/GI via `use_raytracing`, `fast_gi_*`. Cycles remains the reference for bakes.
- `look` names are bare in 5.x (`'Medium High Contrast'`).
- Black render = missing World light, camera not set (`scene.camera`), or inward-facing normals on a one-sided room shell.
- Fireflies from small bright lamps seen through glass: clamp indirect, enable `light.cycles.is_caustics_light=False` (default), avoid glass in front of lights (bake/preview without glazing).
- Portals must face *into* the room (arrow toward interior); mirrored portals = no light.
- Heavy scenes: set `sc.cycles.use_adaptive_sampling=True`, `adaptive_threshold=0.01`.

## Sources
- Cycles manual (portals, sampling) https://docs.blender.org/manual/en/latest/render/cycles/index.html
- Blender colour management https://docs.blender.org/manual/en/latest/render/color_management.html
- Blender 5.0 API notes (EEVEE rename, removed gtao) https://developer.blender.org/docs/release_notes/5.0/python_api/
- Lighting guidance in public skill packs https://github.com/MartinRapcan/blender-claude-skill , https://github.com/arjun988/blender-skills
- Verified on Blender 5.1.1 headless (test_render.py).
