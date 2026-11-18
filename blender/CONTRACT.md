# Build contract — read with spec/BRIEF.md before writing any build code

All build code targets headless Blender 5.1.1 (`.claude/skills/blender-*` hold verified API notes
and helper snippets — read `blender-headless-bpy` first; copy from the skill helpers freely).

## Layout and ownership
```
blender/build.py          entry point (owner: core)
blender/lib/ctx.py        House context (core)
blender/lib/shell.py      walls, openings cut, floors, ceilings, features (core)
blender/lib/lighting.py   world/sky, sun, lamp helpers, render settings (core)
blender/lib/preview.py    cameras + Cycles preview renders (core)
blender/lib/materials.py  material library (materials)        blender/textures/**  (materials)
blender/lib/mouldings.py  profiles, sweeps, cornices, dado, skirting, roses, corbels (joinery)
blender/lib/joinery.py    doors, windows, frames, architraves, doorcases by style key (joinery)
blender/lib/props.py      shared small parts (props)
blender/rooms/<id>.py     one per room id: vestibule hallway stairs living kitchen utility wc dining (room agents)
blender/export.py         lightmap bake, GLB export, plan footprints (export)
tools/plan/               CAD plan drafting -> plan.json, DXF, PDF (plan)
docs/                     static site: index.html, js/, assets/ (viewer)
build/                    git-ignored scratch: .blend files, previews, logs
```
Edit only what you own. If another module needs a change, write the request in your final report.

## Running
```
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$B" -b --factory-startup --python blender/build.py -- [--only shell,living,...] [--save build/home.blend]
     [--preview <room>[,<room>]|all] [--res 960x540] [--samples 64] [--cam <name>] [--tag <suffix>]
```
- `--only` limits which stages run: `shell` (all architecture) and/or room ids (furnishing). Default: everything.
- `--preview` renders every camera in the room module's `CAMERAS` to `build/preview/<room>_<cam>[_<tag>].jpg`.
- `--tag` lets parallel agents keep separate outputs; also use `--save build/<yourname>.blend`.
- Print `BUILD OK` at the end; any exception must exit non-zero (wrap main, `sys.exit(1)`).
- Many agents run builds at once on 2 GPUs: keep previews at ≤960 px / ≤96 samples while iterating.

## ctx (blender/lib/ctx.py)
```python
ctx = House.load()                 # reads spec/house.json
ctx.spec, ctx.rooms[id], ctx.walls[id], ctx.openings[id], ctx.features (list), ctx.stairs
ctx.room_poly(id) -> [(x,y)...]    ctx.floor_z(id), ctx.ceil_z(id)
ctx.col(name) -> bpy Collection    # get/create, linked to scene. Names: 'shell', 'room_<id>'
ctx.add(obj, room, kind, plan_sym=None, lm=None) -> obj
    # links obj into room_<room> (or 'shell' when kind=='shell'); sets custom props:
    #   obj['room']=room, obj['kind']=kind in {'shell','trim','joinery','fit','furn','decor','light'}
    #   obj['plan_sym']=symbol key for the 2D plan (see below) or absent
    #   obj['lm']= 'static' (gets a baked lightmap) | 'dynamic' (lit by probes). Default:
    #             static for shell/trim/joinery/fit, dynamic for furn/decor/light.
ctx.opening_frame(id) -> dict(center, along(unit xy), normal(unit xy), width, height, sill, wall_thickness)
```
Object names: `<room>.<what>[.<n>]`, e.g. `living.sofa`, `kitchen.base.03`. Units metres, apply
scale (object scale 1). Origin placement is free.

## Room modules (blender/rooms/<id>.py)
```python
CAMERAS = [dict(name='door', pos=(x,y,z), look=(x,y,z), fov_deg=75, ref='f_0087'), ...]  # world coords; ref = matching reference frame
def build(ctx): ...   # adds fittings, furniture, decor, light fittings for this room only
```
The shell stage has already built: walls with openings, floor, ceiling, features from
house.json, door/window joinery by style key, skirting/dado/cornice/architraves and wall paint
per the room finish table. Room modules add everything else (cabinetry, appliances, furniture,
art, curtains, light fittings, ceiling rose if not shell, stairs flight for `stairs`). A room
module may restyle shell surfaces of its own room through `shell` helpers documented in
`blender/lib/README.md`, never by editing lib files.

## Materials (blender/lib/materials.py)
- `mat(key) -> Material` cached, e.g. `oak_floor`, `wood_tile_floor`, `victorian_tile`,
  `mahogany`, `oak_door`, `dark_oak_antique`, `brass`, `steel_brushed`, `chrome`, `white_gloss`,
  `velvet_orange`, `tartan_red`, `check_grey`, `carpet_mink`, `marble_quartz`, `marble_metro`,
  `metro_grey`, `oak_worktop`, `glass_clear`, `glass_frosted`, `mirror`, `navy_cabinet`,
  `grey_cabinet`, `ceramic_white`, `black_matt`, `gilt`. `keys()` lists all.
- `paint(hex, roughness=0.9) -> Material` cached per colour; `solid(name, hex, roughness, metallic=0)`.
- `image_mat(name, path, size_m=(w,h)|None, roughness=…)` for art/rug/tile images.
- `uv_box(obj, scale=1.0)` world-scale box-projected UVs (1 UV unit = 1 m × texture `size_m`).
- **glTF rule:** final materials are Principled BSDF with constants and image textures only
  (base colour, ORM, normal). No procedural nodes, no mix shaders. Textures ≤2048 px JPG (PNG only
  for alpha), stored under `blender/textures/`; total texture payload budget 60 MB.
- Colours come from the room specs' neutral-light hex values. sRGB hex → linear is the library's job.

## Mouldings / joinery / props APIs
Owners publish exact signatures in `blender/lib/README.md` (one section per module) — room agents
read that file. Required coverage:
- mouldings: `sweep(profile, path_pts, closed)`; named profiles for every skirting, dado rail,
  cornice (hall modillion, living, dining acanthus, utility/kitchen coving), architrave; ceiling
  roses; scroll corbels; arch/vault helpers; picture-rail.
- joinery: every `style` and `surround` key used in house.json (doors with real panel mouldings,
  glazing bars, handles, hinges; uPVC and timber windows; the pedimented doorcase; dark
  reeded architraves with frieze + cap), honouring hinge/swing/openAngle.
- props: `downlight`, `switch_plate`, `socket`, `framed_picture(image, w, h, frame_style)`,
  `mirror_framed`, `curtain_pair`/`curtain_panel` (pleated, tie-backs), `curtain_pole`,
  `plant_potted`, `handle_bar/knob/lever`, `radiator_*`, `candle_bulb`, `lampshade`, `book_row`,
  `rug(image,…)`, `cushion`, `turned_leg(profile…)`, `lathe(profile, segments)`, `box`, `bevel_box`.

## Geometry budget and quality
- Whole house ≤ 1.8 M triangles in the GLB; living/dining/kitchen ≤ 300 k each, others ≤ 150 k.
- Repeated items (chairs, spindles, crystals, plaques, handles, downlights) are **linked
  duplicates** sharing mesh data. Bevel visible hard edges (2–4 mm, 1–2 segments) — no razor
  edges; smooth-shade curved parts by angle; correct normals (black faces in Cycles = flipped).
- No z-fighting: coplanar overlaps need ≥1 mm offset. Walls are solid; nothing floats.

## Plan symbols (2D plan footprints)
Tag plan-worthy objects via `ctx.add(..., plan_sym=key)`. Keys: `sofa armchair chair stool table
table_round coffee_table console bookcase tv_unit tv rug fireplace base_unit wall_unit tall_unit
worktop hob sink sink_belfast fridge oven_tower washer dryer wc basin radiator towel_rail
mirror plant stair airer shelf`. The export stage writes each tagged object's world XY oriented
bounding box + key to `docs/assets/footprints.json`; the plan drafter draws CAD symbols from it.

## Lighting baseline (lighting.py)
Scene mood: late-afternoon daylight through windows plus all interior lights on, warm white
2700–3000 K (as lived-in). Cycles, AgX view transform, OptiX denoise. Light fittings carry real
emitters sized for Cycles; `lighting.downlight(ctx, room, x, y)` etc. are documented in README.

## Verification (everyone)
Never report success from asserts alone: render previews and Read them next to the reference
frames named in the room spec §9, and iterate until they match in layout, proportion, colour and
detail. State in your report what you verified and what you could not.
