---
name: blender-arch-modelling
description: Use when modelling a realistic building interior in Blender via bpy - walls with door/window openings, cornice/dado/skirting/architrave profile sweeps with mitred corners, panelled doors, bevels, furniture and joinery recipes, real-world UK dimensions, and the canonical house.json that drives both the 3D shell and the 2D floor plan.
---

# Architectural modelling with bpy/bmesh

Helpers in `arch.py` (tested on 5.1.1 via `test_arch.py`): `box`, `cut` (EXACT boolean + apply), `wall` (centre line + openings list), `sweep_profile` (mitred sweep of a 2D profile), `cove`, `SKIRTING`, `DADO_RAIL`, `panel_door`, `join`, `bevel`, `smooth_by_angle`.

## Workflow
1. **Spec first**: read `spec/house.json` (rooms, walls, openings, heights). Generate geometry from it so 3D, 2D plan and viewer minimap share one truth. World: metres, Z up, +Y into the house, origin at the front-door threshold.
2. **Shell**: one object per wall segment via `wall(name, p0, p1, h, thick, openings=[(u, width, sill, head)])`; floors/ceilings as boxes. Door opening sill 0, head 2.1. Interior walls 0.10-0.15 thick, external 0.22-0.34.
3. **Reveals/liners**: add 4 thin boxes (20-25 mm) per opening for jambs/heads, deep sill boards for windows - biggest cheap realism gain.
4. **Mouldings**: `sweep_profile(name, profile, path)`. Path is CCW around the room (left of travel = into the room); path z = base height of the moulding. Cornice = `cove()` or stacked profiles + dentil row (small 25 mm blocks at 50 mm pitch, array modifier); skirting 120-200 mm; dado rail 0.9-1.0 m; picture rail 2.1-2.3 m; architrave 70-100 mm around openings (open path, `closed=False`). Profiles of 5-12 points are enough.
5. **Joinery**: `panel_door` (stile 110, rails 140-160, raised panels 12 mm) + frame; sashes = 4 boxes + glass quad (tint/alpha, not transmission, for web). Pediment = lintel box + triangular prism + two console brackets.
6. **Detail**: `bevel(ob)` (2 mm, angle-limited, harden normals) on joinery/furniture; `smooth_by_angle` for curved profiles. Never bevel walls/floors.
7. **Web budget**: < ~1.5 M triangles; merge per room per material (`join`); repeated items (spindles, tiles) as linked copies; no subdivision left on exported meshes; delete faces hidden behind cabinets.
8. **Naming**: `<room>.<part>[.glass]` - the viewer keys behaviour (glass transparency, lightmap file name) off names.

## Real-world dimensions (UK)
Door leaf 1981x762x35-44; handle 1.0 m; switch 1.2 m; socket 0.3-0.45 m; worktop 0.9 high x 0.6 deep x 38 mm; base units 0.72 + 0.15 plinth, modules 300/400/500/600; wall units 0.72 high x 0.3 deep, bottom at 1.45; hood ~0.65 above hob; washer 0.6x0.6x0.85; American fridge 0.91x0.7x1.78; stair riser 0.19-0.2, going 0.24-0.25, handrail 0.9 above nosing, balusters gap < 0.1; sofa seat 0.42-0.45 high, depth 0.9-1.0, width 2.0-2.2; coffee table 0.4-0.45; dining table 0.75, chair seat 0.45; bookcase depth 0.3-0.35; ceiling 2.6-2.9; cornice drop 0.1-0.15; metro tile 75x150 / 100x200, 2 mm grout; oak plank 180-220 wide.

## Furniture recipes (box + bevel approach)
- Upholstered sofa: base + back + arm boxes, bevel 3-4 cm x 4 segments, optional Subdivision level 1 applied; scroll arms = half-cut cylinders. < 15 k tris.
- Shaker door: 4 rails (60 mm) + 6 mm recessed panel; handles = cylinder bars.
- Chippendale-style chair: tapered legs (box + bevel), seat, back splat as curve with `bevel_depth` or pierced alpha card.
- Glazed bookcase: carcass + shelves + glazing bars + one glass quad; books as a textured strip.
- Fireplace/carved panels: boxes + sweep for mantel; carving via normal map, not geometry.
- Curtains/shutters: plane with sine displacement + Solidify; shutters = slatted boxes.
- Ornaments/plants: simple silhouettes, alpha-card leaves; lowest priority.

## 2D floor plan (feeds the viewer minimap)
Keep `spec/house.json` canonical: `rooms:[{id,name,polygon:[[x,y]..]}]`, `walls:[{a:[x,y],b:[x,y],thickness}]`, `openings`, `bounds:{minX,minY,maxX,maxY}`, `spawn:[x,y]`, all in Blender metres. Build Blender walls FROM it; copy the file next to the GLB for the viewer (`threejs-walkthrough-viewer/plan.mjs` draws it and maps camera pose). In the build, assert each wall bbox in Blender matches the JSON. glTF export converts (x,y,z) -> three (x,z,-y); verified on 5.1.1.

## Gotchas
- EXACT booleans are slow on big meshes: cut per wall, cutters = simple boxes, oversize through-thickness by 1 cm to avoid coplanar faces (`wall()` does).
- `bmesh.ops.create_cube(size=1)` is a unit cube (scale verts, as `box()` does). Run `recalc_face_normals` after hand-built rings; inverted normals look black in Cycles.
- A single-box room shell needs normals flipped inward (back-face culling in the viewer).
- `join` keeps only the active object's modifiers: apply first (or export with `export_apply=True`).

## Sources
- bmesh ops https://docs.blender.org/api/current/bmesh.ops.html
- Boolean solver rename https://developer.blender.org/docs/release_notes/5.0/python_api/
- Breadth of recipes https://github.com/arjun988/blender-skills ; robust geometry/joins https://github.com/MartinRapcan/blender-claude-skill
- Dimensions: UK Building Regs Part K (stairs), standard kitchen/joinery modules, project BRIEF.md.
