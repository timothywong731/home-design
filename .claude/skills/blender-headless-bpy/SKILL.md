---
name: blender-headless-bpy
description: Use when writing, running or debugging Blender Python (bpy) scripts headless on Blender 4.x/5.x - project script structure, CLI invocation, 5.x API breakages (EEVEE id, use_auto_smooth, actions, boolean solver, UV selection), and verifying results by rendering. Read first before any other blender-* skill.
---

# Headless bpy on Blender 5.1

Run (Windows, repo convention): `"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python script.py -- --out build`
- `--factory-startup` = no user prefs/addons surprises. `--` separates your argv (see `boot.py`).
- A Python exception can still leave exit code 0: print an `OK` sentinel and grep the log for `Traceback|Error`. Raise on failed asserts.
- Start from `bpy.ops.wm.read_factory_settings(use_empty=True)` for a deterministic empty scene.
- Prefer data API (`bpy.data.*`, `bmesh`) over `bpy.ops`; ops need context/selection/mode. When unavoidable: deselect all, select + make active, `mode_set('EDIT')` and back (see `blender-pbr-gltf/pbr.py`).
- Structure: one module per concern (`shell.py`, `mouldings.py`, `materials.py`, `bake.py`), a `build_all.py` that does `sys.path.insert(0, dir)`, deterministic (seed any random), idempotent, saves `.blend` into git-ignored `build/`.
- Never use the live Blender MCP in parallel/agent runs: one GUI instance.

## Verify by looking, not by trusting
1. Cheap asserts (`boot.py: sanity`): objects exist, bbox dims in metres, no empty meshes, UV layers present.
2. Low-res preview render from eye-height cameras (`blender-interior-render/render_setup.py`), then Read the PNG. 160x90 @ 16 samples catches missing walls and inverted normals.
3. Export the glb and read its JSON (accessor min/max) to prove final coordinates (see blender-pbr-gltf).

## 5.x API gotchas (checked on 5.1.1 and the official 5.0 notes)
- EEVEE engine id is `'BLENDER_EEVEE'` (was `BLENDER_EEVEE_NEXT` in 4.2-4.5). Read valid values from the enum instead of hardcoding.
- `mesh.use_auto_smooth` removed (4.1). Use `bpy.ops.object.shade_auto_smooth(use_auto_smooth=True, angle=rad)` (adds the "Smooth by Angle" modifier) or `shade_smooth_by_angle`.
- Boolean modifier solver `'FAST'` renamed `'FLOAT'`; use `'EXACT'` for walls/openings.
- Actions are slotted; `action.fcurves/groups/id_root` removed. Use `bpy_extras.anim_utils.action_ensure_channelbag_for_slot()` and `channelbag.fcurves`; `fcurves.new(..., group_name=)`. Avoid keyframes in the model.
- Principled BSDF input names (verified 5.1): `Base Color, Metallic, Roughness, IOR, Alpha, Normal, Diffuse Roughness, Subsurface Weight, Specular IOR Level, Specular Tint, Transmission Weight, Coat Weight, Sheen Weight, Emission Color, Emission Strength`. Old names (`Specular`, `Transmission`, `Emission`) are gone. Find the node by `.type == 'BSDF_PRINCIPLED'`, never by localized name.
- `material.use_nodes` / `scene.use_nodes` are deprecated (always on) - harmless. `scene.node_tree` removed -> `scene.compositing_node_group`.
- Colour management: `view_transform` takes `'AgX'`, `'Filmic'`, `'Standard'`, `'Khronos PBR Neutral'`; **look names are bare** (`'Medium High Contrast'`), not `'AgX - Medium High Contrast'` (4.0/4.1 style) - that raises TypeError.
- Lights: `light.use_temperature/temperature`; portal flag is `light.cycles.is_portal`.
- `ImageFormatSettings.media_type` must be set before `file_format` when switching formats; image-texture node lost `use_mipmap`/`filter_type`; Sky Texture lost `sun_direction`/`turbidity`; `scene.eevee.use_gtao/gtao_*` removed.
- UV selection is shared across UV maps (`BMLoopUV.select` removed).
- Python 3.13 + numpy bundled; use `foreach_get/foreach_set` on `image.pixels`, `mesh.vertices` (50-100x faster than loops).
- If an old snippet fails with "unexpected keyword", list the op's props: `bpy.ops.export_scene.gltf.get_rna_type().properties.keys()`.
- Bake API (`bpy.ops.object.bake(type=..., pass_filter={...}, target='IMAGE_TEXTURES', margin_type='EXTEND')`) did not change in 5.0; see blender-bake-lightmaps.

## Files
- `boot.py` - template entry point (argparse after `--`, reset, sanity checks, save). Tested.

## Sources
- Blender 5.0 Python API release notes https://developer.blender.org/docs/release_notes/5.0/python_api/
- Blender Python API docs https://docs.blender.org/api/current/
- LLM-vs-Blender-5.0 failure survey https://dev.to/rustam335/ask-ten-llms-for-a-blender-50-script-then-run-it-in-blender-50-1pe3
- Public skills reviewed: https://github.com/MartinRapcan/blender-claude-skill (headless bpy), https://github.com/AndreiFlau/blender-mcp-skill (live MCP), https://github.com/arjun988/blender-skills (94-skill pack)
