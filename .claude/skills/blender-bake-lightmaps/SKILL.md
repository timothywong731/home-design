---
name: blender-bake-lightmaps
description: Use when baking Cycles lighting (diffuse direct+indirect, AO) to a second UV channel by script in headless Blender and using it as lightMap/aoMap in three.js, including atlas sizing, margins, denoising, file formats and web delivery.
---

# Lightmap baking (Cycles -> three.js)

Tested helper: `bake.py` (`setup_cycles`, `bake_lightmap(objs, path, size)`), `test_bake.py` (64 px room bake, result non-black, 5.1.1).

## Pipeline
1. Geometry final, materials assigned, normals outward, scale applied.
2. Each mesh has UV layer `UVMap` (tiling textures) + `Lightmap` (0-1, non-overlapping, see `blender-pbr-gltf/pbr.py:lightmap_uv`). Merge per room so each room = one lightmap atlas (typically 2048, hero rooms 4096; < ~64 px/m is blurry; 128-256 px/m ideal for walls/floor).
3. Lights: real fixtures (lamps, chandeliers = emissive meshes or point/area lights), windows via portal area lights + sky/sun world (`blender-interior-render`). Bake the "evening" or "day" state you want baked in; one set only unless you ship two lightmaps and blend.
4. `bake.setup_cycles(samples=256-1024, denoise=True)`; then `bake.bake_lightmap(objs, "build/lm/living.exr", 2048)`.
   - `bake_lightmap` adds an unconnected, *active* Image Texture node (with a float, Non-Color image) to every material of the objects, sets `Lightmap` as the active UV layer, runs `bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT','INDIRECT'}, margin=4, margin_type='EXTEND', use_clear=True, target='IMAGE_TEXTURES')`, saves EXR and removes the nodes.
   - DIFFUSE without `COLOR` = irradiance-like lighting without albedo, which is what three.js `lightMap` expects (it multiplies by the material's diffuse colour). For a full-colour bake instead use `type='COMBINED'` and plug it as an emissive/unlit texture (loses PBR response; not recommended).
   - AO only: `type='AO'` (no pass_filter) -> use as `aoMap`.
5. Ship: convert EXR -> 8-bit sRGB WebP after scaling to fit range (`value = min(1, x/exposure_max)`, remember the divisor and apply it as `lightMapIntensity`) or keep HDR as KTX2/RGBM. A 2048 float EXR is ~16-32 MB; WebP is < 1.5 MB. Do the conversion with numpy/PIL (system Python has both) - run `-I` on untrusted data.
6. three.js: **glTF cannot carry `lightMap`** (only `occlusionTexture`). Export keeps the geometry's second UV as `TEXCOORD_1` (verified), GLTFLoader exposes it as `uv1`. Load lightmap files by mesh name and assign:
   ```js
   tex.channel = 1; tex.flipY = false; tex.colorSpace = THREE.SRGBColorSpace; // LinearSRGBColorSpace for EXR/float
   mat.lightMap = tex; mat.lightMapIntensity = 1; mat.needsUpdate = true;
   ```
   `flipY=false` matches glTF's UV origin; if the bake looks mirrored vertically this is the first thing to toggle. Remove all real-time lights (or keep tiny ambient) to avoid double lighting; `renderer.toneMapping = NoToneMapping` if the bake was already display-referred.
   Intensity calibration: Cycles diffuse bake values are radiance-scale, three.js lightMap is added as irradiance; start with `lightMapIntensity` ~1 for tonemapped-in-Blender WebP, try ~Math.PI if scene looks 3x too dark. UNVERIFIED - compare a screenshot against a Blender render of the same view.
   Alternative: put the lightmap in glTF `emissiveTexture` on UV1 and move it to `lightMap` at load (suggested by three.js maintainers), at the cost of larger GLB.

## Gotchas
- Bake needs an Image node *selected and active* in every material of every baked object; missing -> "No active image found". One image shared by many objects is fine if their `Lightmap` UVs are packed together (atlas): pack ALL objects of a room into one UV space with `uv.pack_islands` in a joint edit session, or bake per object with a per-object image.
- Overlapping `Lightmap` islands or islands outside 0-1 bake garbage. Check with `uv.pack_islands(margin=0.003)`.
- Seams: `margin_type='EXTEND'`, margin >= 4 px at 2k; mipmapped sampling needs margin ~8 px or leaks dark at distance.
- Denoise: `scene.cycles.use_denoising` affects baking in 4.x/5.x; denoise leaks light across islands - prefer high samples + light clamp, and bake with `sample_clamp_indirect=10`.
- Emission-only fixtures need `Emission Strength` > 0 on their mesh; bulbs look black otherwise.
- Bake runs on the *evaluated* mesh; apply modifiers/booleans first so UVs exist.
- GPU: set Cycles device in preferences inside the script (`setup_cycles(gpu=True)` tries OPTIX then CUDA); factory-startup resets prefs each run.
- Time: 2048 px, 512 spp, 2x RTX 4090 ~ minutes per room; use 16 spp 256 px for iteration.

## Sources
- Blender bake manual https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- three.js MeshStandardMaterial lightMap/aoMap https://threejs.org/docs/#api/en/materials/MeshStandardMaterial
- Forum discussion on glTF carrying only AO, lightmap via emissive swap https://discourse.threejs.org/t/why-should-i-use-lightmap-instead-of-draw-shadow-in-diffusemap/46759
- Baked lighting pipeline write-up https://ben3d.ca/blog/building-the-aaa-lighting-pipeline-in-threejs
- Verified on Blender 5.1.1 headless (test_bake.py).
