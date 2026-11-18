---
name: blender-pbr-gltf
description: Use when authoring materials, UVs and textures in Blender that must survive glTF/GLB export to three.js - image-only PBR, ORM packing, normal maps, texel density, scripted UV unwrapping (including a second lightmap UV), export settings, and Draco/meshopt/KTX2 compression with glTF-Transform.
---

# PBR + UV + glTF export

Tested helpers: `pbr.py` (`load_img`, `pack_orm`, `make_material`, `box_uv`, `lightmap_uv`), `export_gltf.py` (`export_glb`), `test_pbr.py` (builds a material, exports, prints the glTF JSON).

## What the exporter understands
- One **Principled BSDF** fed by **Image Texture** nodes. Procedural nodes (noise, bricks, colour ramps, mix) are NOT exported - bake them to images first.
- Base Color tex -> `baseColorTexture`; Normal Map node (tangent space, image set to Non-Color) -> `normalTexture`; Emission Color/Strength -> emissive (+ `KHR_materials_emissive_strength`); Transmission Weight -> `KHR_materials_transmission`; Coat -> clearcoat; IOR, Specular IOR Level -> `KHR_materials_ior/specular`; Alpha -> alpha mode (set material blend mode properly; opaque otherwise).
- **ORM packing (verified 5.1.1)**: one Non-Color image -> *Separate Color* node; Green -> Roughness, Blue -> Metallic, Red -> a node group named `glTF Material Output` with a float input `Occlusion`. Result in the GLB: `metallicRoughnessTexture` and `occlusionTexture` sharing one image. `make_material()` builds this; the group is created by script (`interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')`).
- Opaque materials: `use_backface_culling = True` (else glTF `doubleSided: true`, slower).
- Vertex colours, UV Map nodes (select layer by name) are honoured; unused UV layers are still exported as `TEXCOORD_n` (verified: `Lightmap` layer -> `TEXCOORD_1`), which is what lightmaps need.
- Colour values: textures colour-space correct (sRGB for colour, Non-Color for ORM/normal). Sample real colours from reference then **neutralise warm light cast** before putting them in base colour; albedo of painted walls is rarely above 0.8 or below 0.04.

## Textures
- Budget: 1k-2k per material (4k only for hero floor/rug). Texel density target ~512-1024 px/m for walls/floors, 1024-2048 px/m for hero furniture. Share tiling materials across rooms (UV in metres via `box_uv(size=1.0)`), so one 1k texture covers many m2.
- Prefer seamless tiling textures for paint/plaster/oak/tiles/marble; unique textures only for paintings, tapestry, rug (crops from the video, rectified, no people).
- Generate ORM with `pack_orm(ao, rough, metal, path)`; constants allowed (e.g. `pack_orm(1.0, rough_img, 0.0, ...)`).
- Normal maps: OpenGL (Y+) convention matches Blender and three.js.
- Keep image sizes power-of-two (required for mipmaps on WebGL1 and for KTX2/BasisU block alignment multiples of 4).

## UV by script
- Trim/walls/floors/ceilings: `box_uv(ob, size)` (cube projection, constant density, tiled in metres - no packing).
- Organic/furniture: `bpy.ops.uv.smart_project(angle_limit=rad, island_margin=0.003)` then `pack_islands`.
- Lightmap layer: `lightmap_uv(ob)` makes second layer `Lightmap` non-overlapping in 0-1. Do this per room-merged mesh *after* joining, before baking. UV ops need edit mode + select all (as the helpers do). UV select flags are shared across layers in 5.x.

## Export (verified property names, 5.1.1)
`export_gltf.py:export_glb(path)` sets: `export_format='GLB'`, `export_apply=True` (bake modifiers), `export_yup=True`, `export_texcoords/normals=True`, `export_tangents=False` (three computes them), cameras/lights off, `export_extras=False`, unused images/textures off, `export_image_format='AUTO'`. Draco is `export_draco_mesh_compression_enable=True` but prefer meshopt via glTF-Transform below (Draco decode is slower and breaks with quantised lightmap UVs less predictably).
- Coordinates: Blender (x, y, z) -> glTF/three (x, z, -y). Verified: a 4x3x2.6 box at origin has POSITION min [0,0,-3] max [4,2.6,0].
- Scale: 1 unit = 1 m. Apply scale/rotation on objects before export (`transform_apply`) so normals and bake bounds are clean.
- Exporter writes `KHR_materials_*` only when needed; viewer must use stock `GLTFLoader` (supports them).

## Compression pipeline (after export)
```
npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress webp --texture-size 2048
# GPU-compressed alternative (needs KTX-Software `toktx` on PATH): --texture-compress ktx2
```
- Meshopt (`EXT_meshopt_compression`) is the default geometry compression in `optimize`; viewer needs `MeshoptDecoder`. KTX2 needs `KTX2Loader` + transcoder files; use UASTC for normal/ORM, ETC1S for colour. WebP is simplest on GitHub Pages and 3-5x smaller than PNG; KTX2 wins GPU memory (4-8x less VRAM) - choose KTX2 if the scene exceeds ~250 MB decoded textures.
- `optimize` also welds, prunes, dedups, instances; check it did not merge meshes you key by name (use `--no-join`/`--instance false` flags if names matter; confirm with `gltf-transform inspect`).
- Not verified here: toktx not installed on the dev machine; `npx @gltf-transform/cli` untried offline. Check `gltf-transform optimize -h` for the installed version's flags.

## Gotchas
- A material with an Image node selected as bake target but unconnected is ignored by export; remove bake nodes anyway (bake.py does).
- Mixed procedural + image materials silently export with missing textures: after export, parse the JSON and assert every material has `baseColorTexture` or a deliberate factor.
- Texture names in GLB come from image names: give images meaningful names.
- 5.x: image texture node no longer has `use_mipmap/filter_type`; sampler filtering is decided by exporter (`LINEAR_MIPMAP_LINEAR` default) - set anisotropy in three.js (`texture.anisotropy = renderer.capabilities.getMaxAnisotropy()`).

## Sources
- Blender glTF 2.0 addon manual https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- glTF-Transform CLI https://gltf-transform.dev/cli
- Optimisation overview (Draco/meshopt/KTX2) https://app.cinevva.com/guides/optimize-glb-for-web
- three.js GLTFLoader docs https://threejs.org/docs/#examples/en/loaders/GLTFLoader
- Verified by running tests on Blender 5.1.1 (property lists from live RNA).
