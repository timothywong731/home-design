# blender/lib — API reference for room modellers

Everything a `blender/rooms/<id>.py` module may call. Read with `blender/CONTRACT.md` and
`spec/BRIEF.md`. Units are **metres**, world coordinates: origin = centre of the inside face of the
street-door threshold, **+Y into the house, +X to the right walking in, Z up**, every floor at Z = 0.
Object scale is always 1. All of `blender/build.py` and `blender/lib/**` is owned by the integrator:
room modules never edit lib files — if something is missing, say so in your report.

| section | what |
|---|---|
| [Quick start](#quick-start) | template, single-room preview, cameras, restyling a wall |
| [build.py](#buildpy) | command line, stages, outputs, triangle report |
| [ctx](#ctx-libctxpy) | house.json accessors, `ctx.add`, `opening_frame` |
| [shell](#shell-libshellpy) | what is already built, finishes, `repaint`, `box`, `wall_runs` |
| [lighting](#lighting-liblightingpy) | daylight, emitters for fittings, white balance |
| [preview](#preview-libpreviewpy) | cameras and renders |
| [materials](#materials-libmaterialspy-textures-in-blendertextures) | key list, `paint`, `uv_box` |
| [props](#props-libpropspy) | furniture parts, hardware, pictures, curtains, lamps, plants |
| [mouldings](#mouldings-libmouldingspy) | `MB` mesh builder, profiles, sweeps, room trim |
| [joinery](#joinery-libjoinerypy) | doors, windows, surrounds (already installed by the shell) |
| [export](#export-blenderexportpy-export_bakepy-export_checkpy) | lightmaps, probes, GLB, manifest, footprints, hero stills |

## Quick start

1. Copy `blender/rooms/_template.py` to `blender/rooms/<id>.py` (ids: `vestibule hallway stairs
   living kitchen utility wc dining`), set `ROOM`, replace the body of `build(ctx)`.
2. Preview your room on the real shell, with your own tag so parallel runs do not overwrite each other:
   ```
   B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
   "$B" -b --factory-startup --python blender/build.py -- --only shell,living --preview living --res 540x960 --samples 64 --tag me
   ```
   → `build/preview/living_<camera>_me.jpg`, one per entry of your `CAMERAS`. Add `--cam bay` for a
   single camera, `--save build/me.blend` to keep the scene. A whole-house shell build takes ~3 s,
   each 540x960 / 64-sample preview ~1 s.
3. Read each render next to the reference frame named in the camera's `ref`, fix, repeat.

**A room module is two names:**
```python
from lib import lighting, materials as M, mouldings as mo, props as P, shell

CAMERAS = [dict(name='bay', pos=(2.4, 3.59, 1.5), look=(2.5, 0.0, 1.4), fov_deg=100, ref='f_0791')]

def build(ctx):                     # fittings, furniture, decor and ALL light fittings of this room
    sofa = ...                      # any unlinked bpy object at scale 1
    ctx.add(sofa, 'living', 'furn', plan_sym='sofa')
```

**Adding cameras.** `CAMERAS` entries are dicts `name, pos, look, fov_deg, ref` in world
coordinates; `fov_deg` spans the **longer** image side (the phone's ultrawide is ~100). The
reference frames are portrait, so render with `--res 540x960`. Room specs give camera positions in
room-local coordinates: add the room offset (hallway and stairs `(0, 1.83)`, living `(0.80, 0.99)`,
kitchen mm/1000 + `(1.25, 5.31)`, utility `(0.60, 10.26)`, wc `(0.60, 9.36)`, dining
`(-0.65, 12.36)`, vestibule none). Until a module defines `CAMERAS`, the reference-matched shell
cameras in `preview.DEFAULT_CAMERAS[room]` are used — copy them as a starting point.

**Restyling a wall face of your own room** (never edit `shell.FINISHES` at runtime):
```python
shell.repaint('kitchen', '#F1EFE9', '#EEEEEA')            # swap one finish everywhere in the room -> slots changed
ob = shell.box('kitchen.splash.hob', 4.298, 4.30, 5.31, 8.73, 0.91, 1.50, 'metro_grey')   # x0 x1 y0 y1 z0 z1
M.uv_box(ob, origin=(0, 5.31, 0.91))                      # register the tile joints, see materials
ctx.add(ob, 'kitchen', 'fit')                             # a slab >= 1 mm proud of the plaster
```
`repaint` changes a whole finish (a material slot of `<room>.walls`); to change only part of a wall,
cover it with `shell.box` (splashbacks, nook lining, black soffit) or with your own mesh.

**Rules that bite**
- The shell stage already built: walls, floors, ceilings, doors, windows, frames, architraves,
  skirting, dado, cornice, both ceiling roses, the living picture rail, the dining pelmet and dark
  N screen, hall arch corbels, vestibule imposts/archivolt, thresholds, the brushed-steel trim on top
  of the WC / utility tile dado. Do not add them again.
- Add **every** light fitting of the room: the default fill light is only present while the room
  has no `kind='light'` object.
- Call `M.uv_box(obj)` on any mesh of your own that uses a textured key or matt `paint()`; props and
  `mo.MB` meshes already carry UVs. Never call `uv_box` on a prop (props share mesh data).
- Repeated items must share mesh data: props do it automatically; for your own meshes use
  `new = bpy.data.objects.new(name, first.data)`.
- Budgets (all instances counted): living / dining / kitchen 300 k triangles, other rooms 150 k.
  build.py prints the table (`[build] tris room_living ...`).

## build.py

```
"$B" -b --factory-startup --python blender/build.py -- [--only shell,living,...] [--save build/home.blend]
     [--preview <room>[,<room>]|all|plan] [--res 960x540] [--samples 64] [--cam <name>] [--tag <suffix>]
```
- `--only a,b`: stages to build — `shell` (all architecture, joinery, trim) and/or room ids.
  Default: everything. `--only living` alone builds the module with **no** architecture (fast
  geometry check); use `shell,living` for a real preview.
- `--preview <room>[,..] | all | plan`: renders every camera of the room (its module's `CAMERAS`,
  else `preview.DEFAULT_CAMERAS`) to `build/preview/<room>_<cam>[_<tag>].jpg`. `plan` = top-down
  orthographic view with ceilings hidden → `build/preview/plan[_<tag>].jpg`. `all` = every room + plan.
- `--cam <name>` keeps one camera; `--res WxH` (default 960x540); `--samples` (default 64);
  `--tag` suffixes the preview file names; `--save` path is relative to the repo root.
- Output: `[build] tris <collection> <n> kind=n ...` per collection and a total, then `BUILD OK`.
  A missing room module is skipped silently. An exception in a room module, in joinery or in
  mouldings prints its traceback, the build carries on (previews still render) and ends
  `BUILD FAILED: <what>` with exit code 1. An unknown stage / room name exits 1 immediately.
- Imports inside modules: `from lib import ctx, shell, lighting, preview, materials, mouldings,
  joinery, props` (build.py puts `blender/` on `sys.path`).
- The final acceptance run is
  `build.py -- --only shell --save build/home_shell.blend` → `BUILD OK`.

## ctx (`lib/ctx.py`)

```python
ctx = House.load()                    # spec/house.json; build.py passes the same ctx to every stage
ctx.spec                              # the raw json dict (ctx.spec['ceilingDefault'], ['bounds'], ...)
ctx.rooms[id], ctx.walls[id], ctx.openings[id]      # dicts of the raw json entries by id
ctx.features                          # list of feature dicts;  ctx.feature(fid) -> one of them
ctx.stairs                            # the stairs block (risers, rise, going, newel, landing ...)
ctx.room_poly(id) -> [(x, y), ...]    # inside wall faces, counter-clockwise (piers / breast NOT included)
ctx.floor_z(id), ctx.ceil_z(id)       # 0.0 everywhere; ceilings 2.85 / 2.95 / 2.80 / 2.40 (stairs 5.60)
ctx.room_at(x, y) -> room id | None
ctx.col(name) -> Collection           # get/create: 'shell', 'room_<id>', 'lighting'
ctx.add(obj, room, kind, plan_sym=None, lm=None) -> obj
ctx.opening_frame(oid) -> dict
ctx.errors                            # list of failed stages (build.py)
```
**`ctx.add`** links `obj` **and all its parented children** into `room_<room>` (collection `shell`
when `kind == 'shell'`), unlinks them from any other collection and tags them:
- `obj['room']`, `obj['kind']` ∈ `shell trim joinery fit furn decor light` (child lamps of a prop are
  tagged `light` automatically). `fit` = fixed fittings (cabinets, appliances, sanitaryware,
  radiators), `furn` = loose furniture, `decor` = art, curtains, rugs, ornaments, plants,
  `light` = light fittings and their emitters.
- `obj['plan_sym']` = symbol key for the 2D plan, on the root object only (keys in CONTRACT.md:
  `sofa armchair chair stool table table_round coffee_table console bookcase tv_unit tv rug
  fireplace base_unit wall_unit tall_unit worktop hob sink sink_belfast fridge oven_tower washer
  dryer wc basin radiator towel_rail mirror plant stair airer shelf`).
- `obj['lm']` = `'static'` (baked lightmap; default for shell/trim/joinery/fit) or `'dynamic'`
  (default for furn/decor/light); pass `lm=` to override.

**`ctx.opening_frame(oid)`** — placement frame of a door / window (vectors are `mathutils.Vector`):
| key | meaning |
|---|---|
| `center` | **3D** point on the wall **centreline**, mid-width, z = bottom of the hole (floor + sill). Use `.xy` for 2D |
| `along` | unit xy along the wall a→b |
| `normal` | unit xy **left of a→b**; points into `room_pos` |
| `width`, `height`, `sill`, `head` | clear size above the sill; `head = sill + height` |
| `top` | top of the hole actually cut = max(head, transom.height): the fanlight is part of the same hole |
| `z0` | floor level of the opening |
| `wall_thickness` | of the wall in house.json |
| `face_pos`, `face_neg` | signed distance along `normal` from the centreline to the real wall faces: normally ±t/2; where a `reveal` sets the frame back (`d_back` −0.03, dining N openings +0.07) the face that is actually left |
| `room_pos`, `room_neg` | rooms on the +normal / −normal side |
| `swing_sign` | +1 leaf swings to +normal, −1 to −normal, 0 none |
| `virtual` | True for `o_stair_foot` (nothing is cut) |
| raw json | `type style surround hinge hingeAt openAngle transom connects notes ...` |

Example — a switch plate 0.15 m beside the living-room door on the living side:
```python
f = ctx.opening_frame('d_living')
n = f['normal'] * (1 if f['room_pos'] == 'living' else -1)          # wall normal into the living room
p = f['center'].xy + n * abs(f['face_pos']) - f['along'] * (f['width'] / 2 + 0.25)
sw = P.place(P.switch_plate(2), (p.x, p.y, 1.2), facing=tuple(n))
ctx.add(sw, 'living', 'fit')
```

## shell (`lib/shell.py`)

`shell.build(ctx)` builds all architecture from `spec/house.json`, then calls
`joinery.install_openings(ctx)` once and `mouldings.install_room_trim(ctx, room)` for every room.
Everything in house.json is axis-aligned, so the shell is box CSG on a non-uniform grid
(`ctx.grid`), not booleans: walls, room voids, features and openings are rasterised and only the
boundary faces are emitted as large quads (~1.5 k triangles). Every face knows which room it faces
and takes that room's finish.

**Objects** (collection `shell`, `obj['kind'] = 'shell'`, `obj['room']`, `obj['part']`):
| name | content |
|---|---|
| `<room>.walls` | every vertical face seen from the room, reveals of its openings, soffits, feature faces; one material slot per finish |
| `<room>.floor` | floor incl. the half of each door opening on that side; true-scale UVs (`rotate=True` when `floor.direction == 'x'`) |
| `<room>.ceiling` | 0.12 slab over the room, underside = ceiling colour (`obj['part'] == 'ceiling'`, hidden in the plan render) |
| `hallway.arch_fill`, `vestibule.vault_fill` | curved infill of the hall arch and the vestibule basket vault |
| `shell.exterior`, `shell.wall_tops` | outside faces (flat brick-ish placeholder) and wall tops (dark, plan poche) |
| `shell.threshold.<opening>` | where two floor finishes meet: hardwood bar 75 x 8 mm (`d_kitchen`, `d_utility`); flush mahogany sill 100 x 2 mm under the inner screen (`d_inner`) |
| `shell.ground` | outdoor ground plane, `obj['no_export'] = True` |

**Already built — do not build again**
- Openings: rectangular holes `width` x (`sill`..`top`), filled by joinery (frames, linings, leaves,
  glass, architraves, sills). Door leaves stand at the `openAngle` of house.json.
- Hall arch (infill, springing 2.40, crown 2.75; corbels by mouldings). Vestibule piers, vault
  haunches and the mass above; imposts and archivolt by mouldings.
- `reveal` features cut back into the wall: `kitchen_backdoor_reveal`; `dining_n_screen` (the whole
  dining N wall is recessed 0.22 up to 2.38 and lined with the dark timber screen by joinery).
- `kitchen_nook` recess with its soffit at 2.03; WC and utility bulkheads; WC cistern duct (tiled,
  ledge at 1.20); dining chimney breast and hearth slab (20 mm, `hearth_marble`); hall pilasters
  and nib.
- Stairwell (for `rooms/stairs.py`): walls to 5.60 with a cap, half-landing slab (x 0.15..0.99,
  y 8.13..8.73, top 2.85, soffit 2.60), the bulkhead on x = 0.15 north of y 7.58, corner post
  0.10 x 0.10 at (0.15, 7.63) to the hall ceiling, T&G boarding band 2.07–2.30 and the overhead
  cupboard carcass above the under-stairs door. The carcass top is stepped (2.40 south of riser 14,
  2.59 north of it) and the under-stairs wall stops at 2.20, so both stay below treads 12–14: **the
  flight must cover them.** Treads, risers, landing carpet, strings, balustrade, newel, spandrel
  panelling, the raking dado and its grey band are all `rooms/stairs.py`. Stair-side walls are
  plain white `#F2F0EA`. Skirting already runs along the spandrel foot (x = 0.15, y 5.33..7.58).
- **Not built anywhere** (room modules): kitchen and utility splashback tiles, the nook tiles and
  black soffit lining, the kitchen cornice notch round the hood chimney, brass door stops / cabin
  hooks, the lamb's-tongue chamfers on the living bay nibs.

**Finishes** — `shell.FINISHES[room]` (also `shell.finish(room)`):
```python
dict(upper='#..', lower='#..',      # wall finish above / below the dado split (equal when no dado)
     dado=0.965, dado_h=0.07,       # TOP of the dado rail and its height; None = no dado
     ceiling='#..', joinery='#..',  # ceiling colour; colour of painted trim in this room
     faces=[dict(axis=0, at=0.80, mat='#9E6E60', range=(lo, hi)?, z=(z0, z1)?)],   # per-face overrides
     wainscot=(1.20, 'marble_metro') | None,       # tile on every wall face below z
     features={'wc_cistern_duct': 'marble_metro'})  # per-feature material
```
A material spec is `'#RRGGBB'` (matt paint) or a `lib.materials` key. `shell.split_z(room)` =
height where `lower` changes to `upper` (hidden behind the rail) or None.
| room | walls | ceiling |
|---|---|---|
| vestibule, hallway | `#F2F0EA` over `#C8C5BB` below the dado (rail top 0.965; lightened from the specs' `#B9B5A8` to match f_0770 / f_0548) | `#F4F3EE` |
| stairs | `#F2F0EA` | `#F4F3EE` |
| living | `#EADFD9` blush pink; W (TV) wall x = 0.80 `#A27365` terracotta (both eased from living.md toward the frame samples) | `#F6F4EF` |
| kitchen | `#F1EFE9` | `#F5F4F0` |
| utility | `#F1F0EB`; hall-side wall x = 0.60, y 11.17..12.23 tiled `marble_metro` floor→1.39 | `#F6F5F2` |
| wc | `#A5A5A8` over `marble_metro` to 1.20 on all walls and the duct | `#F6F5F2` |
| dining | `#DFD8CB` over `wallcovering_aubergine` below the dado (rail top 1.05) | `#F3F1EB` |

Floors: `oak_floor` (hall, stairs, living, dining; boards along Y), `wood_tile_floor` (kitchen,
utility, wc; planks along Y), `victorian_tile` (vestibule, blue square registered on (-0.045, 0.025)
via `shell.FLOOR_ORIGIN`). Skirting, dado and cornice **profiles** live in `mouldings.TRIM`.

**Helpers**
```python
shell.surface(room, part='walls') -> Object | None      # part: walls | floor | ceiling
shell.repaint(room, old, new, part='walls') -> int      # swap one finish (specs or Materials) -> slots changed
shell.box(name, x0, x1, y0, y1, z0, z1, spec) -> Object # world-aligned slab with material + uv_box UVs, NOT linked
shell.material(spec) -> Material                        # '#RRGGBB' -> M.paint, else M.mat(key)
shell.wall_runs(ctx, room, z=0.05) -> [loop, ...]       # loop = [((ax, ay), (bx, by), kind, opening_id), ...]
shell.wall_rect(ctx, wall) -> (x0, x1, y0, y1)          # plan rectangle of a wall incl. corner extensions
shell.poly_rects(poly) -> [(x0, x1, y0, y1), ...]       # rectilinear polygon -> rectangles
```
- `repaint` example: `shell.repaint('wc', '#A5A5A8', '#9FA0A6')`. It swaps the material in every
  slot of `<room>.walls` that uses `old`, so it changes that finish on all walls of the room.
- `box` example (utility splashback on the rear wall, 2 mm proud, joints registered to the worktop):
  `ob = shell.box('utility.splash', 0.60, 3.10, 12.228, 12.23, 0.91, 1.50, 'marble_metro');
  M.uv_box(ob, origin=(0.88, 0, 0.91)); ctx.add(ob, 'utility', 'fit')`.
- `wall_runs`: outline of the room's clear space at height `z` *including* piers, pilasters, the
  chimney breast, boxings and reveals, walked with the room on the LEFT (outer loop
  counter-clockwise, the direction `mouldings.sweep` wants). `kind == 'wall'`: solid behind the
  run; `'open'`: a door / window hole (`opening_id`) or an open room boundary (`None`). Example —
  a picture rail at 2.2 m: `for loop in shell.wall_runs(ctx, 'dining', 2.2): ...` and sweep the
  `'wall'` runs.

## lighting (`lib/lighting.py`)

`lighting.setup(ctx, samples, res)` (called by build.py after the rooms are built) = Cycles on all
OptiX GPUs with the OptiX denoiser, AgX + look `Medium High Contrast`, plus daylight.
| constant | value | meaning |
|---|---|---|
| `EXPOSURE` | -0.6 EV | view exposure |
| `WHITE_BALANCE`, `WHITE_TINT` | 3000 K, -10 | preview white point = the lamps, like the phone at night: a `#F2F0EA` wall renders ≈ `#B9B4A8` (video ≈ `#BDB9AF`). View setting only |
| `SUN_DIR`, `SUN_STRENGTH`, `SUN_KELVIN` | (-0.38, 0.72, -0.58), 2.5, 3600 K | low sun through the bay and the east flank windows |
| `SKY_COLOR`, `SKY_STRENGTH` | (1.0, 0.86, 0.74), 0.22 | world background: a dim dusk sky (reads deep blue-grey through the lamp white balance; the video is shot at night) |
| `FILL_W_PER_M2`, `FILL_UP_W_PER_M2`, `FILL_PITCH` | 30, 2.5, 1.3 m | default fill per room: wide downward spots on a grid 0.35 m under the ceiling (lit like the real downlights, so floors and the wall below the dado get their share) + one soft point light per rectangle for the ceiling |

A Cycles portal sits just inside every external opening (collection `lighting`).

Emitters for light fittings — each returns the light object, linked and tagged `kind='light'`:
```python
lighting.downlight(ctx, room, x, y, z=None, watts=60, kelvin=2850, spot_deg=115, radius=0.035, name=None)
    # spot pointing straight down; z defaults to ceiling - 15 mm. Emitter only: pair with props.downlight (trim)
lighting.bulb(ctx, room, loc, watts=12, kelvin=2700, radius=0.025, name=None)
    # point light: 8-12 W per chandelier candle bulb, 25-40 W for one table lamp / pendant
lighting.strip(ctx, room, p0, p1, watts_per_m=10, kelvin=3000, width=0.012, direction=(0, 0, -1), name=None)
    # LED strip between two world points (under-cabinet, shelf), shining along `direction`
lighting.fill(ctx, room) -> [objects]
    # default fill (obj['fill'] = True, invisible to camera and reflections); build.py adds it only
    # to rooms that have no kind='light' object
```
- Watts are Blender radiometric watts tuned for `EXPOSURE`: six 60 W downlights in the kitchen
  (3.05 x 3.42) expose about like the default fill. Two 40 W downlights make the WC visibly dim.
- Example: `for x, y in [(2.0, 6.2), (3.5, 6.2)]: lighting.downlight(ctx, 'kitchen', x, y)` plus
  `ctx.add(P.place(P.downlight(), (x, y, ctx.ceil_z('kitchen'))), 'kitchen', 'light')` for the trim.
  Chandelier: `for p in P.bulb_points(root): lighting.bulb(ctx, 'dining', p, watts=10)`.
- Keep emitters ≥ 2 cm clear of geometry; do not put emissive meshes inside glass shades (use a
  `bulb` and let the shade be plain geometry).
- A `bulb` at `P.bulb_points` sits **inside** the opaque emissive lamp mesh of the prop: it only
  shines while its `radius` (default 0.025) is larger than the lamp. A smaller radius is silently
  blocked (a whole chandelier goes dark) — keep the default or move the light clear of the lamp.
- Emission is **not** white-balanced like reflected lamp light: an emissive colour paler than about
  `#FFC489` renders blue-white in the previews. Author lit shades / strips warm (e.g. `#F4CB94`).
  The viewer applies no white balance to emissive factors, so these read more amber there (export / viewer note).
- **Export / bake:** lamps are 2700–3000 K blackbodies, i.e. orange in a D65 pipeline; previews look
  right only because of the view white balance. Lightmaps are baked without view settings, so apply
  the same white balance to them. Skip `obj['fill']` lights and `obj['no_export']` objects.

## preview (`lib/preview.py`)

```python
preview.DEFAULT_CAMERAS[room] -> [dict(name, pos, look, fov_deg, ref), ...]   # shell review cameras, world coords
preview.default_cameras(ctx, room)                                  # the same list
preview.camera(name, pos, look, fov_deg=75) -> camera Object        # fov_deg spans the longer image side
preview.render(cam_obj, path, res=(960, 540), samples=64)           # JPEG; path must be absolute
preview.render_room(ctx, room, cams, out_dir, res, samples, tag=None, only=None) -> [paths]
preview.render_plan(ctx, path, res=(960, 540), samples=64, cut_z=1.5)
```
- `DEFAULT_CAMERAS` holds 2–6 cameras per room matched to the reference frames of
  `spec/rooms/<id>.md` §9 (e.g. hallway `inner front doorcase arch lobby rear`, living `bay tvwall
  north baycorner`, dining `entry east north south nw`); `ref` names the frame.
- `render_plan`: orthographic top view, +Y up, ceilings hidden, sectioned at z = 1.5 by camera
  clipping — openings show as gaps, door leaves at their modelled angle, cut walls as black poche.
  About 540 x 1600 px.
- From a scratch script on a saved `.blend`: `bpy.ops.wm.open_mainfile(...)`,
  `lighting.setup_cycles(samples, res)`, then `preview.render(preview.camera('c', pos, look, 100),
  abs_path, (540, 960), 64)`. Always pass absolute output paths: Blender resolves relative render
  paths against the drive root.

## materials (`lib/materials.py`, textures in `blender/textures/`)

```python
from lib import materials as M
M.mat(key) -> Material            # cached library material; also accepts the house.json names
                                  # oak_plank, victorian_geometric_tile, wood_effect_porcelain_plank, carpet_mink_grey
M.keys() -> [str]                 # every key mat() accepts (65)
M.paint('#RRGGBB', roughness=0.9) -> Material     # cached per colour+roughness; M.PAINT = named room colours
M.solid(name, '#RRGGBB', roughness, metallic=0) -> Material     # plain constant colour, cached by name
M.image_mat(name, path, size_m=(w, h) | None, roughness=0.8) -> Material   # art / rug / tile picture
M.uv_box(obj, scale=1.0, rotate=False, origin=(0, 0, 0))        # world-scale box UVs, see below
M.hex_lin('#RRGGBB') -> (r, g, b, 1) linear
```
Every material is one Principled BSDF with constants + image textures (base colour sRGB, ORM
G=roughness B=metallic, tangent normal OpenGL), so it exports to glTF as is. Hex colours are sRGB;
the library converts to linear. Each material has `mat['size_m'] = (w, h)`: the real-world size
of one texture repeat. Names in the GLB = the key (`paint_F2F0EA_r90` for paints).

**`uv_box`** writes the first UV layer (`UVMap`): every face is projected along its dominant world
axis, UV = world metres / (`size_m` of that face's material × `scale`). Textures therefore show
at true size, stay continuous across neighbouring objects, and one mesh may mix materials. It
reads loc/rot/scale directly, so it is correct straight after `obj.location = ...`. Call it after
the mesh and its material slots are final (it works on the base mesh, not on modifier output).
- Floors/ceilings: U = +X, V = +Y. Walls: U = horizontal, V = +Z. Never mirrored.
- **Direction convention:** timber grain, floor boards, plank tiles and worktop staves run along
  **V** (world Y on a floor, vertical on a wall/door stile). Metro tile courses and brushed-steel
  streaks run along **U** (horizontal on walls). `rotate=True` turns the texture 90° (boards along
  X; horizontal grain on rails, drawer fronts, table tops running along X).
- `origin=(x, y, z)`: the world point that lands on UV (0, 0) — registers a joint or motif.
  `victorian_tile` has its blue square at UV (0.5, 0.5): for blue squares centred on world
  (bx, by) use `origin=(bx - 0.165, by - 0.165, 0)`. Metro tiles: v = 0 is the centre of a
  horizontal joint; the course just below it (and every second course) has vertical joints at
  u = 0 + n x 0.303 m, the course just above is offset half a tile (course pitch 0.103 m;
  `marble_metro` 0.3025 / 0.1025).
- `image_mat(..., size_m=None)` is for pictures that fill a face once: give that mesh its own
  0..1 UVs (uv_box would repeat it every metre).

**Textured keys** (size = metres per repeat; colour = spec hex the texture mean was matched to):
| key | size_m | maps | colour | rough | notes |
|---|---|---|---|---|---|
| `oak_floor` | 2.2 x 4.4 | 2048² col+nrm+orm | #AF9F66 | 0.38 | golden straw engineered oak (renders ≈ `#B1A47C` like f_0064), straight grain + cathedral figure, boards 220 mm, 1.2–2.2 m, micro-bevel, board-to-board tone steps, ~1 brown knot per board |
| `wood_tile_floor` | 1.221 x 3.61 | 1024x2048 col+nrm+orm | #807A62 | 0.45 | weathered grey-brown porcelain planks 200x1200, soft low-contrast weathering, plank-to-plank tone steps, 3.5 mm grout #CFCABB (kitchen/utility/WC) |
| `victorian_tile` | 0.33 x 0.33 | 1024² col+nrm+orm | 4 colours | 0.45 | vestibule floor, from the spec's cell table |
| `metro_grey` | 0.909 x 0.618 | 1024² col+nrm+orm | #C4C2BD | 0.12 | 300x100 half-bond, 3 mm white grout (kitchen) |
| `marble_metro` | 0.9075 x 0.615 | 1024² col+nrm+orm | #EFEDE8 | 0.12 | 300x100 half-bond Carrara print (soft grey veins #A3A3A0 on about every other tile), grout #C9C7C0 (utility/WC) |
| `sunflower_tile` | 0.152 x 0.152 | 512² col+nrm | — | 0.10 | dining fireplace tile strips, one tile per repeat |
| `marble_quartz` | 2.4 x 1.2 | 2048x1024 col | #F2F1EE | 0.10 | kitchen worktop, wide forked diagonal veins #9E9A92 |
| `hearth_marble` | 1.2 x 1.2 | 1024² col | #E2DCCF | 0.25 | dining hearth slab |
| `oak_worktop` | 1.0 x 1.8 | 1024² col | #B38E58 | 0.42 | utility stave worktop, staves 40 mm |
| `oak_door` `oak_rustic` `oak_light` `oak_table` `dark_oak_antique` | 1.2 x 1.2 | 1024² col + shared nrm | #A7954E #A98850 #C9A877 #5E4631 #3A2A1E | 0.3–0.5 | door leaves (golden oak, renders ≈ `#A88E52` like f_0499; 0.42); TV unit; bare carcass; dining/coffee table top; antique dark oak furniture + fire surround |
| `dark_joinery` `hardwood_threshold` | 1 x 1 | 1024² col + shared nrm | #40342C #54351F | 0.25 / 0.4 | dining stained joinery + living bay timber; threshold bars |
| `mahogany` `mahogany_dark` `mahogany_mid` | 1 x 1 | 1024² col + shared nrm | #4A2216 #3B241A #6A452C | 0.12 / 0.25 | gloss inner doors, newel, handrail; chairs, sofa frame, bookcase; polished mid-brown tops |
| `navy_cabinet` `grey_cabinet` | 1 x 1 | 1024² col + shared ash nrm | #23252D #BDBDB8 | 0.40 | painted ash-grain shaker cabinets |
| `velvet_orange` `velvet_orange_light` `velvet_champagne` | 0.284 x 0.2735 | 1024² col + shared nrm, sheen | #B5683F #C98958 #D3C6A6 | 0.85 | sofa/chairs/stools; scatter cushions; vestibule stool lid |
| `tartan_red` | 0.2 x 0.2 | 1024² col+nrm | yarns #8E8271 #A04A45 #E3DCCB #3C3836 | 0.95 | living curtains, 2/2 twill sett |
| `check_grey` | 0.2 x 0.2 | 1024² col+nrm | #E7E1D3 / #9A9382 / #7F7868 | 0.95 | dining curtains |
| `tapestry_floral` | 0.3 x 0.3 | 1024² col+nrm | ground #EBE4D0 | 0.90 | dining chair seats (generic Jacobean floral, not a crop) |
| `linen_cream` `shade_ivory` | 0.271 | 1024² col + shared nrm | #E6D9B8 #F0E6CF | 0.90 | gimp braid / cord / tie-backs; lampshades |
| `wallcovering_aubergine` | 0.54 | 1024² col + shared nrm | #44333A | 1.0 | dining wall below the dado (woven, dead matt, violet cast) |
| `carpet_mink` | 1 x 1 | 1024² col+nrm, sheen | #9C958A | 1.0 | stair carpet |

**Constant-colour keys** (no UVs needed unless noted): metals `brass` `brass_antique`
`bronze_antique` `bronze_dark` `gilt` `gilt_bright` `gold_champagne` `chrome` `silver_satin`,
`steel_brushed` `nickel_brushed` (shared streak nrm+orm, 0.3 m, wants uv_box); blacks `black_matt`
`black_gloss` `screen_black` `cast_iron` `anthracite` `slate_black`; whites `white_gloss`
(joinery) `white_satin` (shutters) `plaster_white` `upvc_white` `plastic_white` `ceramic_white`;
`pot_jade` `pot_olive` `alabaster` `cork`; `mirror`; glass `glass_clear` `glass_frosted`
`glass_obscure` (stipple nrm, 0.15 m) `glass_green` `glass_dark` `whisky` (decanter contents).
`mat()` raises `KeyError` for an unknown key and `FileNotFoundError` for a missing texture — nothing
falls back silently.

**Glass / mirror (export + viewer please note).** Glass is alpha-blended, not transmissive:
`glass_clear` = metallic 1, roughness 0, alpha 0.10 (a 10 % mirror: daylight passes in Cycles
without caustics; glTF gets `alphaMode: BLEND`, double-sided, no `KHR_materials_transmission`).
Frosted/obscure/green/dark are dielectric with alpha 0.6–0.9. Use thin single-surface panes.
`mirror` = metallic 1, roughness 0 (reflects the environment map in three.js; swap for a
Reflector by material name if wanted). Velvet and carpet export `KHR_materials_sheen`.

**Paint.** `paint(hex)` with roughness ≥ 0.6 carries one shared faint roller-stipple normal map
(1 m repeat; `M.PAINT_STIPPLE = False` before the first call turns it off); gloss paint is plain.
`M.PAINT` (name → hex): `hall_white hall_dado_grey joinery_white ceiling_white living_terracotta
living_pink living_ceiling kitchen_white kitchen_ceiling utility_white utility_ceiling wc_grey
wc_ceiling dining_cream dining_ceiling`, e.g. `M.paint(M.PAINT['living_pink'])` — the same colours
the shell uses.

**Textures.** `python -I blender/textures/gen/fetch.py` (Poly Haven CC0 sources → `build/texsrc/`)
then `python -I blender/textures/gen/make_all.py [woods tiles fabrics misc]` rewrites
`blender/textures/*.jpg`, `manifest.json` (files, `size_m`, measured mean colour per key) and
`SOURCES.md`. 57 JPGs, 9.7 MB, all power-of-two ≤ 2048, quality 88. Art/rug crops belong in
`blender/textures/art/` and go through `image_mat`.
**Test.** `blender -b --factory-startup --python blender/textures/test_swatches.py -- [--close key,key]`
→ `build/materials/swatch_NN.jpg` (1 m plane + sphere per key, labelled), `swatches.glb`, and a
check that every material kept its textures in the GLB; prints `SWATCH OK`.

## props (`lib/props.py`)

`from lib import props as P`. Shared small parts; every call below was built, rendered in Cycles and
looked at (contact sheet, see **Test**). All sizes metres.

**Rules that apply to every prop**
- Returns **one unlinked object**, scale 1, UVs present (`UVMap`), materials assigned — hand it to
  `ctx.add(obj, room, kind)` after setting `location` / `rotation_euler`. Every prop also accepts
  `name='living.sofa.cushion.01'` (keyword only).
- **[H] = hierarchy**: the returned root has parented children (linked sub-parts and/or lights).
  `ctx.add(root, room, kind)` links and tags the children too (child lamps become `kind='light'`);
  `P.family(root)` lists root + descendants.
- **Mesh sharing is automatic**: the same arguments (however they are spelled) return a new object
  on the *same* mesh datablock — 30 handles = 1 mesh. Different `seed` / size = new mesh.
- **Origins**: floor props = centre of the footprint at z = 0. Wall props = centre of the back
  face; back on local y = 0, front faces local **-Y**, +X to the viewer's right, nothing pokes
  behind y = 0. Ceiling props = contact point, hanging -Z. Exceptions are stated per prop.
  `P.place(obj, (x, y, z), facing=(nx, ny))` sets the location and turns the front toward a wall
  normal (e.g. `ctx.opening_frame(id)['normal']`, or `(1, 0)` for a wall whose room side is +X);
  `P.place(obj, loc, rot_z=deg)` for free-standing things.
- **Materials**: any `mat` / `finish` / colour argument takes a `lib.materials` key, `'#RRGGBB'`
  (paint), a props extra key, or a `bpy` Material; an unknown key raises `KeyError`. Props extras
  (constant colours, `P.mat(key)`): `gold_antique gold_bronze olive_bronze silver_green frame_dark
  walnut plastic_dark ivory cream_mount tassel_gold soil bark leaf_green leaf_mid leaf_lime
  leaf_grey fruit_orange terracotta marble_green dial_cream cone_grey skin_ref`. Shorthands
  `antique_brass gold_bright champagne silver rope_cream` resolve to the library's `brass_antique
  gilt_bright gold_champagne silver_satin linen_cream`. `finish` shorthands: `brass antique_brass
  black steel chrome white gilt bronze`. Library colours always win: `brass` is `#D3C882` (the
  reflectance of polished brass; the specs' `#C9A44C` as a metallic base rendered copper-orange), `gilt`
  is `#A2924A` (use `gilt_bright` for `#B8A655`). All gold / brass bases are olive-yellow on purpose:
  orange-leaning ones render copper / rose beside coloured walls under the 3000 K view.
  UVs are in metres divided by the material's `size_m` (same convention as `materials.uv_box`,
  in object space: grain vertical on upright faces); picture / rug images use 0..1 UVs.
- **Double-sided**: library materials cull back faces in the GLB. Single-surface parts (curtain
  cloth, leaves, unlit shades, the cup pull) therefore use `P.two_sided(mat)` → a cached copy
  `<name>_2s` with culling off. Use it yourself for any other open surface.
- **Emitters**: lit lamps and downlight lenses are emissive meshes (`P.emissive(hex, strength)`,
  constant Principled emission, glTF-safe). Real Cycles lights are **off by default** (`watts=0`)
  so they are not doubled with `lighting.*`: either pass `watts=` (child lights, [H]) or do
  `for p in P.bulb_points(root): lighting.bulb(ctx, room, p, watts=10)` / `lighting.downlight(...)`.
- Budget helper: `P.tris(obj)` (all instances) / `P.tris(obj, unique=True)`.
- Helpers: `P.mat(spec)`, `P.two_sided(mat)`, `P.emissive(hex, strength)`, `P.image_mat(path,
  rough=.6)`, `P.family(obj)`, `P.bulb_points(obj) -> [Vector]` (world), `P.place(obj, loc,
  facing=(nx, ny) | rot_z=deg)`.
- Example: `tv = P.tv_panel(1.45, 0.83, name='living.tv'); P.place(tv, (0.80, 2.6, 1.35),
  facing=(1, 0)); ctx.add(tv, 'living', 'fit', plan_sym='tv')`.

### Generic parts
```python
P.lathe(profile, segments=16, mat='brass', smooth=True)   # profile [(r, z)...] bottom -> top, r=0 closes on the axis
P.box(w, d, h, mat='white_gloss')                          # 12 tris, origin bottom centre
P.bevel_box(w, d, h, mat='white_gloss', bevel=.003, segments=1)   # 1 = flat chamfer (44 tris), 2+ = rounded
P.turned_leg(height, width=.06, style='baluster', top_block=0.0, bottom_block=0.0, mat='dark_oak_antique',
             segments=12, pitch=.16, starts=2, out=(1, -1), foot='claw', taper=.6)
P.baluster(height=.9, width=.032, base_block=.18, top_block=.12, mat='white_gloss', style='spindle')
P.turned_profile(style, height, width, z0=0.0) -> [(r, z)]      # feed to P.lathe / customise
```
`turned_leg`: origin floor centre, axis +Z. `width` = side of the square stock = size of the
optional square joint blocks (`top_block` / `bottom_block` heights); the turning may be fatter.
`style`: `P.TURNINGS` keys `baluster spindle bobbin bun cup_cover vase column`, or
- `'barley_twist'` — rope column, `pitch` = height of one full turn, `starts` ropes (dining
  fireplace columns: `turned_leg(.6, .11, 'barley_twist')`; side-table legs with blocks);
- `'cup_cover'` — Elizabethan melon bulb, gadrooned cover, 1.7 x width at the girdle (dining table:
  `turned_leg(.73, .13, 'cup_cover', .12, .14)` → 0.21 bulb);
- `'cabriole'` — S-leg, knee toward `out` (xy, e.g. `(1, -1)` = front-right corner),
  `foot='claw'` ball-and-claw or `'pad'`; give it a `top_block`;
- `'taper'` — square tapered leg, foot = `taper` x width.

### Cabinetry and hardware
```python
P.panel_door(w, h, t=.02, stile=.085, rail=None, recess=.006, bead=.012, mat='navy_cabinet',
             panels=(1, 1), slab=False, edge=.002)
P.cabinet_carcass(w, d, h, mat='navy_cabinet', plinth=.15, plinth_recess=.04, open_front=False,
                  shelves=0, panel=.018, inner=None)
P.handle_bar(length=.22, centres=.16, dia=.012, standoff=.032, finish='antique_brass', vertical=False)
P.handle_knob(dia=.03, projection=.03, finish='antique_brass')
P.handle_cup(width=.096, height=.04, projection=.026, finish='antique_brass')
P.handle_lever(length=.12, finish='brass', rose=.052, hand=1)       # hand=-1: lever points -X
P.handle_d(length=.13, dia=.01, projection=.03, finish='brass', vertical=False)
P.handle_drop(width=.07, drop=.035, finish='black')                 # bail on two rosettes
```
- `panel_door`: shaker front = frame + recessed flat panel with a sloped inner bead. `stile` =
  vertical members (and muntins), `rail` = horizontal members (default = stile), `panels=(cols,
  rows)`, `slab=True` (or a front too small for a frame) = flat slab. Origin: **bottom centre of
  the back face**, front at y = -t. 44 tris.
- `cabinet_carcass`: origin floor centre on the wall plane; box spans y 0..-d, z plinth..h, recessed
  plinth below (`plinth=0` for wall units — then set the object's z). `open_front=True` = real
  18 mm panels, back and `shelves` (bookcase, wine rack, plate rack), lined with `inner`.
- Handles: origin on the door face, centred. A base unit is three calls:
```python
c = P.cabinet_carcass(.6, .58, .87)                       # at (x, y_wall, 0)
d = P.panel_door(.597, .712)                              # at (x, y_wall - .58, .15)      (local coords shown)
h = P.handle_bar(vertical=True)                           # at (x + .245, y_wall - .60, .15 + .545)
```

### Electrical
```python
P.downlight(dia=.085, lamp_dia=.05, watts=0.0, kelvin=3000, spot_deg=110, strength=12.0, trim='plastic_white')
P.switch_plate(gangs=1, kind='rocker', finish='white', wide=None, h=.086)
P.socket(gangs=2, switched=True, finish='white', h=.086)
```
- `downlight`: white trim ring + emissive lens, all within 5 mm below the ceiling plane (origin).
  `watts > 0` adds a child SPOT [H]; otherwise pair it with `lighting.downlight`.
- `switch_plate`: `kind` `'rocker' | 'dimmer'` (round knobs) `| 'push'` (small round buttons) `|
  'toggle'` (dolly) `| 'blank'`. 86 x 86, or 146 x 86 when `wide` (default: 3+ gangs of
  dimmer/push/toggle). `finish='white'` moulded plastic, or `'brass' / 'antique_brass' / 'chrome' /
  'black'` flat metal plate.
- `socket`: UK 13 A, `gangs` 1 (86 wide) or 2 (146 wide), pin slots + rockers; same finishes.

### Pictures, mirrors, rug, plaques, A/V
```python
P.framed_picture(image=None, w=.6, h=.5, frame_style='gilt_plain', frame_w=None, depth=None, mount=0.0,
                 glass=False, slip=None, mount_mat='cream_mount', tilt_deg=0.0, fill=None)
P.mirror_framed(w=1.2, h=.85, frame_style='gilt_ornate', frame_w=None, depth=None, bevel=0.0, tilt_deg=0.0)
P.rug(image=None, w=1.4, d=2.0, thickness=.008, fringe=0.0, corner_r=0.0, color='#E4DDC8', fringe_mat='ivory', seed=0)
P.wall_plaque_shield(w=.15, h=.18, shape='heater', variant=0, board=None, colors=None, image=None,
                     thickness=.02, scroll=True)
P.tv_panel(w=1.89, h=1.08, depth=.03, standoff=.04, bezel=.005)
P.speaker_box(w=.21, h=.33, d=.27, mat='black_matt', drivers=2)
```
- `framed_picture`: `w, h` = **outer** frame size. `image` = file path (absolute, or as
  `materials.image_mat` accepts), shown once over the picture window, upright (verified with a test
  card); `None` = neutral 3-band landscape placeholder (`fill=(ground, mid, sky)` hex) — use that
  for the dining mantel portrait. `frame_w` / `depth` override the style defaults. `mount` = mount
  width in m (`True` = auto), `slip=(material, width)` = coloured inner fillet, `glass=True` adds a
  glazing quad, `tilt_deg` tips the top forward about the bottom back edge (gallery pictures: 3).
- `P.FRAME_STYLES` (default width x depth mm):
  `gilt_ornate` 95x45 rippled swept moulding + corner/centre cartouches (~4-5 k tris) ·
  `gilt_swept` 80x40 same without cartouches (~2.5-3 k) · `gilt_plain` 60x30 scoop ·
  `gilt_bead` 60x30 reeded with inner bead · `gilt_thin` 15x20 · `champagne` 60x30 scoop ·
  `bronze_gold` 60x30 scoop · `silver_green` 45x25 scoop · `dark_wood` 45x25 flat ·
  `dark_gold_slip` 55x28 dark with gold inner slip · `walnut_gold` 28x20 walnut with gold sight
  edge · `olive_bronze` 42x20 flat · `white` 30x20 · `black` 20x20. Plain styles are 50-120 tris.
- `mirror_framed`: same frames round a real `mirror` plate; `bevel` = bevelled-edge width.
- `rug`: `w` along X, `d` along Y, image u→X v→Y over the whole rug (image top = +Y end);
  `fringe` = strand length on the two short ends; `corner_r` rounds the corners. Origin floor
  centre; underside floats 1.2 mm above z = 0 (no z-fight).
- `wall_plaque_shield`: bevelled board (`shape` `'heater' | 'round' | 'lozenge'`) + raised crest.
  `variant=i` deterministically varies board tone, partition (plain / chief / per pale / per
  fess), colours and emblem (disc, cross, lozenge, star) — pass the plaque index for 36 different
  ones; `colors=(field, second, emblem)` overrides; `image=` maps a rectified crop over the board
  front instead. `round` gets a gilt rope ring + crown. 150-520 tris.
- `tv_panel`: origin wall, **screen centre**; back of the panel `standoff` off the wall.
- `speaker_box`: origin bottom centre, front -Y.

### Curtains, poles, shutters
```python
P.curtain_panel(width=.5, height=2.4, mat='tartan_red', folds=None, depth=.06, tieback=None, tie_from_top=1.4,
                gather=.6, tassel=.30, seed=1, fold_res=6, tie_mat='rope_cream', tassel_mat='tassel_gold')
P.curtain_pair(width=1.8, height=2.4, mat='tartan_red', stack=.5, tieback=True, tie_from_top=1.4, gather=.6,
               hang='pole', depth=.06, tassel=.30, seed=1, fold_res=6, hang_mat=None, finial='ball',
               tie_mat='rope_cream', tassel_mat='tassel_gold')
P.curtain_pole(length=2.0, dia=.028, finial='ball', rings=12, mat='brass', standoff=.075)   # finial 'ball' | 'urn'
P.pelmet_box(length=2.0, height=.2, depth=.14, mat='white_gloss')
P.tassel(length=.30, head_dia=.06, mat='tassel_gold')                # origin = hanging point
P.plantation_shutter_panel(w=.4, h=1.5, stile=.05, rail=.09, louvre=.063, thickness=.028, tilt_deg=40,
                           mid_rail=None, mat='white_gloss', tilt_rod=True)
```
- `curtain_panel`: one drop. **Origin: wall plane, top centre of the heading**; cloth hangs to
  z = -height, 12–90 mm in front of y = 0 (up to ~140 mm at a tie-back bunch). `width` = hanging (stack) width, `folds` = number of
  pleats (default width / 0.11), `depth` = fold depth; tight pencil pleats at the heading opening
  into full folds. `tieback='left' | 'right'` = side the bunch is pulled to **as seen from the
  room**: the far edge sweeps across, the cloth pinches at `tie_from_top` below the heading to
  `gather` x width, the hem lifts slightly, and a rope loop + wall hook + tassel (`tassel` =
  length, 0 = none) is added. Spec → call: top z 2.50, tie z 1.00, stack 0.50, bunch 0.30 →
  `curtain_panel(.5, 2.49, 'check_grey', tieback='left', tie_from_top=1.5)` placed at z = 2.50.
  UVs follow the cloth (fullness 2), so tartan/check setts keep their true 0.2 m size.
  ~2 k tris per 0.5 m drop (lower `fold_res` from 6 to 4 for far or half-hidden drops).
- `curtain_pair`: two drops, each `stack` wide, at the ends of a `width` span, tied outward.
  `hang='pole'` (brass pole + rings + finials, 0.15 overhang, axis 40 mm above the heading) |
  `'pelmet'` (boxed pelmet 0.2 high) | `'track'` | `None`. Same origin as `curtain_panel`.
- `curtain_pole`: origin wall plane at pole-axis height. `pelmet_box`: origin wall, top centre.
- `plantation_shutter_panel`: one leaf, origin **bottom centre, mid-plane on y = 0**; `mid_rail` =
  z of an optional mid rail; ~800 tris per 1.5 m leaf.

### Radiators
```python
P.radiator_towel_rail(w=.4, h=1.2, groups=(8, 7, 5), pitch=.04, bar_dia=.022, standoff=.08, mat='anthracite', valves=True)
P.radiator_panel(w=1.0, h=.6, depth=.1, standoff=.03, mat='white_gloss', valves=True, floor_gap=.15)
```
Origin of both: **wall plane, bottom centre of the radiator body** (WC rail: z = 0.18). `groups` =
bars per group from the bottom up. Valves/tails hang ~55 mm below the origin; the panel radiator's
pipes run `floor_gap` down to the floor.

### Plants
```python
P.plant_potted(kind='monstera', height=None, spread=None, pot_dia=.2, pot_h=.18, pot_mat='terracotta', seed=1,
               leaves=None, stand=0.0, stand_mat='dark_oak_antique')
```
`kind`: `'monstera'` (split leaves on arching stems, default 0.60 high x 0.55 wide, 9 leaves) |
`'dracaena'` (two canes, striped strap rosettes, 1.10 x 0.75) | `'citrus'` (bare stem, round leafy
head with fruit, 1.75 x 0.70) | `'eucalyptus'` (sparse drooping stems, 0.50 x 0.35 — WC ledge).
`height` / `spread` = overall incl. pot and `stand` (a low wooden disc under the pot). Leaves are
solid low-poly meshes (no alpha), two-sided materials. 1.0–1.8 k tris. Origin floor centre.
Pots: use `pot_mat='pot_jade'` / `'pot_olive'` / `'black_matt'` / `'brass'`.

### Light fittings
```python
P.candle_bulb(height=.09, dia=.025, sleeve='ivory', lit=True, watts=0.0, kelvin=2700)
P.lampshade(top_dia=.07, bottom_dia=.15, height=.13, style='scalloped', color='#F0E6CF', lit=True,
            trim='tassel_gold', panels=6)
P.crystal_drop(length=.06, kind='spear', mat='glass_clear')          # 'spear' | 'tear' | 'ball'; origin = top
P.bead_swag(span=.3, sag=.06, bead=.01, mat='glass_clear')           # from the origin to (span, 0, 0)
P.chandelier_arm(reach=.4, rise=.1, dip=.06, mat='brass', pan_dia=.055, candle_h=.09, bobeche_dia=0.0, drops=6,
                 drop_len=.06, shade=None, pendant=0.0, lit=True, scroll=True, watts=0.0, kelvin=2700)
P.chandelier(dia=.8, drop=.55, arms=8, upper_arms=4, upper_dia=.44, upper_rise=.12, mat='brass', body='column',
             shade=None, crystals=True, rise=.1, watts=0.0, kelvin=2700, lit=True)          # [H]
P.sconce(arms=2, width=.36, height=.33, projection=.16, mat='brass', shade=None, lit=True, watts=0.0, kelvin=2700)
```
- `shade` (arm / chandelier / sconce) = `(top_dia, bottom_dia, height, style, colour)`, e.g. dining
  `(.07, .15, .13, 'scalloped', '#F0E6CF')`, living `(.07, .13, .11, 'pleated', '#B4605A')`.
  `lampshade` styles: `'empire'`/`'drum'` smooth, `'panel'` flat panels, `'pleated'`, `'scalloped'`
  (wavy lower edge); `lit=True` = softly emissive cloth; origin = centre of the bottom rim.
- `candle_bulb`: ivory sleeve + flame lamp, origin base of the sleeve, total height + 65 mm.
- `chandelier_arm`: **one complete light** — S-scroll arm, drip pan, candle, lamp, optional glass
  bobeche with `drops` spear crystals, tear `pendant`, shade. Origin = hub attachment, arm along
  +X ending at `(reach, 0, rise)`. Build your own fitting by instancing it round a hub
  (`rotation_euler.z = 2*pi*k/n`); identical args → one mesh (~600 tris plain, ~1.1 k dressed).
- `chandelier` **[H]**: ceiling cup + turned stem + hub + finial (root mesh), `arms` lower arms on
  `dia`, `upper_arms` on `upper_dia` raised `upper_rise`, bead swags between lower arm tips.
  `body='column'` (crystal column, crystal ball finial) | `'bowl'` (dished brass bowl, acorn
  finial). `drop` = ceiling to lowest point. Origin: ceiling contact. Dining:
  `chandelier(.8, .55, shade=(.07, .15, .13, 'scalloped', '#F0E6CF'))`; living:
  `chandelier(.85, .8, body='bowl', crystals=False, shade=(.07, .13, .11, 'pleated', '#B4605A'))`;
  a lantern-less 6-arm: `chandelier(.47, .69, arms=6, upper_arms=0, body='bowl', crystals=False)`.
  15 k tris all instances / 3 k unique with crystals, 9.4 k / 2.2 k without. `watts` = per lamp.
- `sconce`: oval backplate + urn finial + `arms` candle arms spread over `width`, standing
  `projection` off the wall. Origin wall, backplate centre. ~1.6 k tris.

### Books, upholstery
```python
P.book_row(length=.8, height=.22, depth=.15, seed=0, fill=1.0, palette=None)
P.cushion(w=.45, h=.45, thickness=.14, mat='velvet_orange', piping=None, res=8)
P.bolster(dia=.17, length=.4, mat='velvet_orange', button='rope_cream')
P.upholstered_seat(w=.5, d=.45, thickness=.08, style='plain', mat='velvet_orange', buttons=(4, 2), crown=.012,
                   edge=None, piping=None, gimp=None)
```
- `book_row`: varied thickness / height / depth / colour (`palette` = hex list) with gilt bands.
  Origin: shelf surface, centre of the row; spines face -Y at y = -depth. `fill` < 1 leaves a gap
  at the +X end (last book leans). Reuse a `seed` to instance a row, change it for variety.
- `cushion`: pillow shape lying flat, origin centre of the underside (rotate about X to lean it
  on a sofa back); `piping` = cord material. 256 tris.
- `bolster`: axis along X, origin centre of the underside.
- `upholstered_seat`: pad with soft top edges and crowned top; `style='buttoned'` adds
  `buttons=(across, deep)` dimples + buttons; `piping` / `gimp` = material of a welt cord round
  the top edge / braid band round the bottom. Origin bottom centre. 430 tris plain.

### Glassware and ornaments
```python
P.tumbler(height=.09, dia=.075, sides=10, mat='glass_clear')
P.wine_glass(height=.2, bowl_dia=.085, mat='glass_clear')            # rotation_euler.x = pi to hang it bowl-down
P.decanter(height=.3, kind='square', mat='glass_clear', liquid='whisky', level=.55)   # kind 'square' | 'round'
P.glassware_set(tumblers=6, with_decanter=True, tray=(.5, .35), tray_mat='silver', glass_h=.09)   # [H]
P.mantel_clock(w=.32, d=.16, h=.37, style='slate', mat=None, dial_dia=None)
P.vase(height=.3, dia=.16, kind='baluster', mat='ceramic_white', flowers=0,
       flower_colors=('#D9482B', '#E88A2E', '#E06A8A'), seed=0)
P.plate(dia=.27, mat='ceramic_white', height=.022)
P.human_ref(height=1.7, mat='skin_ref')                              # preview-only scale mannequin
```
- `mantel_clock`: `'slate'` = black architectural case (stepped plinth, green colonnettes, stepped
  top with low dome, cream dial in a brass bezel — dining mantel); `'bracket'` = wooden bracket
  clock (stepped top, brass carrying handle, square brass dial, silvered chapter ring — living
  bookcase: `mantel_clock(.26, .15, .30, 'bracket')`). Origin bottom centre, front -Y.
- `vase` kinds: `baluster urn bottle bowl cylinder planter`; `flowers=n` adds simple blooms.
- `plate`: lies flat, origin centre of the base; `rotation_euler = (pi/2, 0, pi/2)` stands it on
  edge across a rack (lift it by dia/2).
- All glass is single-surface `glass_clear` (alpha-blended in the library).

### Test
`blender -b --factory-startup --python blender/lib/props.py -- --out build/props [--res 1600x900]
[--samples 64] [--only A,B2,D]` builds every prop in four bays with a 1.7 m mannequin, renders
`build/props/props_<bay><n>.jpg` (A turnings / cabinetry / hardware, B wall-hung, C soft
furnishings, D lighting / ornaments / plants; `--only none` skips rendering), writes
`build/props/tris.txt` (per-prop triangle table) and ends with `PROPS SHEET OK` (asserts: scale 1,
UVs, finite coords, mesh sharing, `bulb_points`). Whole sheet: 93 k tris.

## mouldings (`lib/mouldings.py`)

Called by the shell: `install_room_trim(ctx, room_id)` for every room. **Room modules must not add
skirting, dado, cornice, the two ceiling roses, the living brass picture rail, the dining pelmet,
the hall arch corbels or the vestibule imposts/archivolt again** - they are built here (kind
`trim`, names `<room>.skirting|dado|cornice`, `living.rose`, `living.picture_rail`, `dining.rose`,
`dining.pelmet`, `hallway.arch_corbels`, `vestibule.arch_mouldings`, `wc.tile_trim`,
`utility.tile_trim`). The picture rail hangs at z = 2.70, 100 mm below the cornice. The tile trims are
10 mm brushed-steel strips on top of the tile dado (`mo.TILE_TRIM`: WC all walls + duct ledge at 1.20,
utility hall-side wall at 1.39).

```python
from lib import mouldings as mo
mo.PROFILES[key] -> [(d, h), ...]      # metres; mo.profile_size(key) -> (projection, height)
mo.sweep(profile, path, closed=False, name='sweep', material='joinery_white', up=(0, 0, 1)) -> Object
                                       # profile = key or [(d, h)...]; path = [(x, y, z)...]; NOT linked
mb = mo.MB()                           # mesh builder: several primitives -> one object, material slots
mb.at(Matrix=None)                     # transform for what follows (None = identity; mirrors are handled)
mb.box(a, b, mat, bev=0.0, grain=None)                 # cuboid between corners a, b; bev = chamfer; grain axis 0|1|2
mb.sweep(profile, path, mat, closed=False, up=(0, 0, 1), caps=True, ends=(None, None))
mb.prism(base_pts, vec, mat, grain=None)               # planar polygon extruded along vec
mb.lathe(profile_rz, mat, segs=24, ell=(1, 1), a0=0, a1=2*pi)   # revolve [(r, z)...] round local Z
mb.tube(path, r, mat, n=8, closed=False, up=None)      # round bar along a polyline; loop in a plane: up=<plane normal>
mb.dome(rx, ry, h, mat, segs=8, rings=3)               # half-ellipsoid on the local XY plane
mb.leaf(length, width, relief, mat, segs=6, serrate=0.0, curl=0.0, base=0.25, rib=0.55, round_=0.6, skew=1.0)
mb.face(pts, mat, hint=None, grain=None)               # one planar polygon, normal toward `hint`
ob = mb.finish(name, matrix=None, sharp_deg=35.0)      # -> Object, NOT linked: pass to ctx.add(ob, room, kind)
mo.mat(key)                            # mo.MATS key (below) or any lib.materials key -> Material
mo.tri_count(objects) -> int
```
- **Material keys for `MB`** (`mo.MATS`): `joinery_white` (= `white_gloss`), `plaster_white`,
  `upvc_white`, `oak` (= `oak_door`), `mahogany`, `dark_stain` (= `dark_joinery`), `threshold`,
  `shutter_white`, `brass`, `chrome`, `black`, `red_plastic`, `flap_smoked` (cat-flap doors), `glass`,
  `glass_frosted`, `glass_obscure`, `glass_smoked`; any `lib.materials` key or a Material object also works.
  `MB` UVs are in metres (V along the grain / along the sweep) and are divided by the material's
  `size_m` in `finish()`; `mb.box(a, b, mat, bev, grain=axis)` sets the grain axis (0/1/2).
  `mb.finish(name, matrix=None, sharp_deg=35)` returns an unlinked, smooth-shaded object.
- **Example.** `mb = mo.MB(); mb.box((0, 0, 0), (1.2, 0.3, 0.03), 'oak', bev=0.002);
  ob = mb.finish('living.shelf'); ob.location = (2.0, 4.70, 1.1); ctx.add(ob, 'living', 'fit')`.
  A dado-height rail on one wall: `ob = mo.sweep('dado_hall', [(0.99, 5.4, 0.9), (0.99, 7.5, 0.9)])`
  (the profile projects to the LEFT of travel).
- **Sweep convention.** Ring point = `P + d*side + h*up`, `side = up x travel`. With `up=+Z`, `d`
  is to the LEFT of travel, so a counter-clockwise room path puts `d` into the room and path z is
  the base of the moulding (floor for skirting, `top - height` for dado, the ceiling for cornices:
  their `h` is negative). Corners are mitred (inside and outside); open ends are capped. Raking
  rails: same call with a sloping path (plumb mitres at the knees). The end polygon of a profile that
  starts on the wall and ends on the ceiling / floor (cornice, skirting) is closed through that corner
  and faces outward. In a wall plane pass
  `up=<wall normal>` (architraves, archivolts, raking pediment cornices). List profile points
  counter-clockwise round the solid seen with travel pointing at you, e.g. skirting from
  `(thickness, 0)` up to `(0, height)`. `mo._q/_s/_half` build quarter-rounds, cymas and beads.
- **Profiles** (`mo.PROFILES[key]`, projection x height mm; aliases `skirting_<room>`,
  `coving_kitchen`, `coving_utility` exist): skirting `sk_vest` 200x22,
  `sk_hall`/`sk_kitchen` 170x20, `sk_living`, `sk_utility` 170x18, `sk_dining` 150x22 (dark);
  dado `dado_hall` 70x30 torus rail (top 0.965), `dado_dining` 55x22 reeded (top 1.05); cornices
  `cornice_hall` 220x200 modillion, `cornice_living` 150x130, `cornice_kitchen` 110 cove,
  `cornice_utility`/`cornice_wc` 80x80 + ceiling band, `cornice_dining` 150x130 acanthus band;
  architraves `arch_hall` 70, `arch_living` 100, `arch_kitchen` 80, `arch_utility` 72,
  `arch_hall_dining` 85, `arch_vest_window` 75, `arch_dark` 110 reeded, `arch_dark_window` 100;
  caps `dark_cap`, `ped_bed`, `ped_shelf`, `ped_cornice`, `ped_cap`; `impost_vest`, `archivolt`,
  `bay_sill`, panel beads `bead_bolection`, `bead_ovolo`.
- `mo.cornice(mb, key, path, closed)` sweeps a cornice and adds its enrichment: fluted modillion
  blocks (55x70x60 at ~0.13 centres, set out per wall leg, clear of the mitres) for the hall, the
  leaf-and-dart relief band (75 mm repeat, real low-relief mesh, no textures) for the dining room.
  `mo.stations(path, closed, pitch, dm)` gives the block set-out; `mo.modillion(mb)` one block.
- `mo.ceiling_rose(style, name) -> Object` (origin at the ceiling, relief down): `'acanthus_whorl'`
  dia 0.75 (living: 8 + 16 lobed leaves with midrib and spine, leaf relief 46 / 28 mm), `'floral_dish'`
  dia 0.80 (dining: band of 36 broad touching leaves with bosses, bead ring, three three-tier blooms,
  relief ~45 mm). Installed centres: `mo.ROSE_AT` =
  `{'living': (2.55, 2.86), 'dining': (1.225, 14.61)}` - hang the chandeliers there.
- `mo.arch_corbel(mb, length, proj, height)` (hall arch: stepped cap, neck, cavetto sweeping back on
  three sides to a slender shaft with three pointed flutes per face, drop block),
  `mo.scroll_corbel(mb, w, h, proj)`
  (doorcase console), `mo.shell_scroll_ornament(mb)`, `mo.fluted_body(...)`,
  `mo.arch_points('segmental'|'basket', x0, x1, springing, crown, n)` -> intrados `[(x, z)]`,
  `mo.brass_rail(points, name)` (gallery rod with cup brackets + finials; brackets go to the LEFT
  of travel).
- **Room trim.** `mo.TRIM[room][kind]` = `dict(profile, top (dado), mat, solids, skip, only)`.
  `mo.room_loops(ctx, rooms, z, solids)` = outline of the clear space at height z (room polygons
  minus walls, piers, pilasters, chimney breast, boxings, low soffits; arches open below the
  springing); `mo.trim_runs(ctx, rooms, z, cfg)` = that outline cut at door/window surrounds
  (`mo.surround_reach`), `reveal` features and the cfg boxes, as mitre-ready runs. Skirting stops
  at architraves, dado at architraves and at windows it crosses, cornices run unbroken round
  breasts / piers / bulkheads. Hall specifics are in the table: nib return included, stair wall and
  spandrel left to `rooms/stairs.py` (skirting IS run along the spandrel foot, x = 0.15), no
  cornice on the arch wall, the inner screen or the open stairwell; the dining N cornice sits on
  the pelmet front. Kitchen/utility skirting only on the exposed lengths (`only` boxes).
- Not built here (owners: room modules): raking dado + wall string on the stairs (use
  `PROFILES['dado_hall']` with a sloping path), spandrel panelling, T&G boarding, the kitchen
  cornice notch round the hood chimney, chamfer stops on the living-room nibs.

## joinery (`lib/joinery.py`)

Called by the shell: `install_openings(ctx)` builds every opening in house.json;
`build_opening(ctx, oid)` builds one; `validate(ctx)` lists unknown style/surround keys.
Objects: kind `joinery`, named `<room>.<opening id>.<part>`: `lining` / `frame`, `surround`
(one per side, in that side's room), `leaf[.0|.1]`, `...glass` (separate objects, glass materials),
`timber` / `shutters` (bay), plus `dining.screen` and `living.bay.sill`.
- **Holes.** The shell cuts each hole exactly `width` x (`sill`..`top`). Linings are 4 mm skins on
  the hole faces; leaves are the hole width less ~7 mm each side; uPVC door frames add a flange on
  the room face (street 1.24 wide, back door 0.95), the mahogany screen caps the wall stubs.
- **Leaves** are separate objects whose **origin is the hinge axis** (rotate about local Z to
  animate); custom props `door` (opening id), `open_deg`, `hinge_side`. They honour `hinge`
  ("left/right seen from the room the leaf swings into"), `swingInto`, `openAngle`; double doors
  take per-leaf angles from `joinery.LEAF_ANGLE` (`d_inner`: west leaf 85, east shut). The pocket
  door stands `joinery.POCKET_PROJECT` (0.09 m, as filmed in f_0499) out of its pocket (0.61 =
  shut); props `slide`, `projects`.
- **Styles:** `oak_4panel` (raised-and-fielded panels, bolection beads, brass lever on backplate,
  3 brass butts), `oak_glazed` (two frosted lights over two panels), `mahogany_glazed_double`
  (frame wall to wall, clear fanlight, 2x5 bevelled panes, arched top rail, long backplates,
  keyhole on the east leaf, flush-bolt knobs), `white_glazed_double` (street: Georgian bars 3x4 in
  obscure glass, letterbox + cylinder on the west leaf, plain frosted transom with NO lettering,
  vent hoods, flag hinges; `french_door`: clear lights, fanlight, round cat flap in the west leaf;
  both pairs have a rebated meeting stile: cover strips on the west leaf lap the east leaf, no gap),
  `white_back_door` (half glazed, toplight, cat flap: white frame, smoked arched flap, red lock), `pocket_oak` (oak lining, dark slot,
  flush pulls), `white_upvc_fixed|obscure|casement`, `dark_timber_white_upvc_shutters` (bay: dark
  posts / mullions / transom / head / sill board, white lights, top-hung fanlights, 6 louvred
  shutter panels, shut: 63 mm blades at 75 deg, overlapping; the head board stops under the cornice;
  the west return, seen from the vestibule, has fixed lights with a slim 22 mm sightline).
- **Surrounds:** `plain_architrave` (profile per room via `mo.architrave_key`; kitchen side has
  plinth blocks), `pediment` (`joinery.doorcase_pediment`), `dark_architrave` and `dark_aedicule`
  (`joinery.dark_surround`: reeded legs, frieze, returned cap; aedicule adds apron, sill board,
  dark reveal), `dark_screen` (whole dining N wall, built once with `d_french`), `mahogany_frame`,
  `white_upvc_frame`, `plaster_reveal`, `flat_white_surround`, `white_architrave_two_lights`
  (vestibule side of the bay return: one 75 mm architrave + reveal lining per light, glass ~0.43 wide),
  `dark_timber`.
- Reusable parts: `joinery.side_frame(fr, sgn)`, `architrave(mb, key, hw, top)`,
  `returned(mb, prof, u0, u1, yb, z, mat)`, `lever_handle`, `flush_pull`, `butt_hinges`,
  `leaf_oak_4panel(mb, gb, w, h)`, `upvc_light(...)`, `hang_leaf(...)` - see the docstrings.
- Not built here: thresholds (shell), brass door stops / cabin hooks, curtains, the street canopy.
- Triangles: trim + joinery of the whole house = 107 k (hallway 51 k, dining 30 k, living 15 k).
- Scratch harness: `blender -b --factory-startup --python build/joinery_test/t.py -- --cams
  doorcase,bay,...|all` renders close-ups to `build/joinery_test/out/` and checks every hinge axis
  against `hingeAt`.

## export (`blender/export.py`, `export_bake.py`, `export_check.py`)

Turns a saved build into everything the viewer loads. Driven only by the custom props `obj['lm']`,
`obj['room']`, `obj['kind']`, `obj['plan_sym']`, `obj['no_export']` — never by object names.

```
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$B" -b --factory-startup build/home.blend --python blender/export.py -- --out docs/assets
     [--bake-res 2048] [--samples 256] [--density 160] [--probe-res 1024] [--rooms a,b] [--skip-bake] [--renders]
```
| flag | meaning |
|---|---|
| `--bake-res` | largest lightmap atlas side (default 2048) |
| `--samples` | Cycles samples for lightmaps and probes (default 256); hero stills use `max(256, samples)` |
| `--density` | lightmap texels per metre aimed for (default 160); each atlas is the power of two nearest to it, capped by `--bake-res` |
| `--rooms a,b` | bake / render only these rooms (`shell` = the exterior atlas); the others keep their images from the existing `manifest.json`. Only valid while the other rooms' geometry is unchanged |
| `--skip-bake` | no lightmaps or probes (old manifest entries are kept): GLB + manifest + footprints in ~15 s |
| `--renders` | hero stills into `<out>/../renders` |

Ends with `EXPORT OK` (exit 1 + traceback otherwise). Needs `npx` (Node) for glTF-Transform 4.5.1.
- **Iterating:** the defaults. Shell only (102 k triangles), 2 x RTX 4090: 66 s in all (2048 px / 256 spp
  bake 6 s per room, probe 2 s, GLB 7 s). Walls and floors are clean; thin mouldings look mottled
  (100 px/m is 2 texels across a 2 cm facet).
- **Publishing:** `--bake-res 4096 --samples 1024 --renders`. 4 min 17 s without the stills (4096 px
  atlas 41-55 s), + 4.5 s per still. Living, dining and hallway get 4096 px atlases (200-220 px/m), the
  others 1024-2048; lightmaps 8.1 MB instead of 3.5 MB. This is what is in `docs/assets` now.

**Output** (`<out>` = `docs/assets`)
| file | content |
|---|---|
| `home.glb` | all meshes except `no_export`; +Y up; node `extras` = the custom props; `TEXCOORD_0` tiling UVs, `TEXCOORD_1` lightmap UVs on lightmapped objects; no lights / cameras; meshopt + `KHR_mesh_quantization`, colour textures WebP, normal / ORM maps JPEG |
| `lightmaps/<room>.jpg` | one atlas per `obj['room']` (`shell` = exterior faces and wall tops at a third of the density) |
| `probes/<room>.jpg` | equirect panorama per house.json room |
| `manifest.json` | `lightmaps [{room, image, objects[], intensity, size, pxPerM}]`, `probes [{room, image, pos [x, y, z], intensity}]`, `rooms [{id, name, polygon, ceilZ, floorZ}]`, `spawn {pos, yaw}`, `toneMapping`, `exposure` (2^EV of the scene view settings), `encoding` (text), `glb` (counts, size) |
| `house.json` | `spec/house.json` without the `notes` fields |
| `footprints.json` | `[{name, room, plan_sym, obb [[x, y] x4], zmin, zmax, height}]` for every `plan_sym` object: minimum-area rectangle of its and its children's vertices in world XY (axis-aligned unless a turned one is smaller) |
| `../renders/<room>_<cam>.jpg`, `index.json` | 1920 x 1080 Cycles stills `[{file, room, title}]` from the room module's `CAMERAS`, else `preview.DEFAULT_CAMERAS`; field of view capped at 90 deg (the cameras are ultrawide portrait matches) |

**Encoding of lightmaps and probes.** 8-bit sRGB JPEG, `linear = srgbDecode(pixel) * intensity`.
`intensity` = 99.5th percentile of the lit texels, at most 6 x their median (hot spots beside lamps
clip; one 8-bit step is about 2 % at the median), with 1 LSB triangular dither against banding.
Lightmaps hold Cycles DIFFUSE direct + indirect **without albedo**, i.e. the radiance of a white
surface: three.js wants `lightMapIntensity = PI * intensity`, `texture.channel = 1`, `flipY = false`,
sRGB colour space. Probes are plain radiance (no PI), image centre = +X, increasing u turns towards
-Y: the three.js equirect layout after the (x, z, -y) axis swap, no rotation needed. The scene's view
white balance (3000 K, tint -10) is multiplied into both (matrix measured through Blender's own
display pipeline), so the viewer shows them like the previews with `toneMapping` / `exposure` of the
manifest and no extra colour correction.

**What gets a lightmap** (`export_bake.classify`)
- `lm == 'static'` meshes, grouped by `obj['room']`. They are re-tagged before export, so the GLB
  extras carry the final value:
- static objects with less than 0.05 m2 of surface (handles, hinges, switch plates, downlight
  trims) or made only of metal / glass become `lm = 'dynamic'`: a lightmap cannot light a material
  without a diffuse lobe, and these objects keep their instancing and get the room probe instead.
- **Linked duplicates that stay static are made single-user.** Lightmap UVs live in the mesh, so
  each instance needs its own copy to get its own texels; the triangle count is unchanged, only
  the sharing is lost. Linked duplicates that are dynamic stay shared (one glTF mesh, many nodes).
- All modifiers are applied first; objects sharing a mesh and an identical modifier stack share
  the applied mesh.

**Lightmap UVs** (`export_bake.unwrap`): layer `Lightmap`, always the second one (a mesh without
UVs gets an empty `UVMap` first; extra layers beyond the first are dropped). Smart-project at
66 deg on welded temporary copies (the library meshes split vertices at hard edges, which would make
every moulding facet its own island), ring-shaped islands (skirting loops, architraves, frames) cut
into solid strips, equal texel density, AABB packing with a gap of 1/512 of the atlas (4 px at
2048). The layout does not depend on the bake resolution and is deterministic (two runs give a
byte-identical GLB). Measured on the shell: fill 0.32-0.79; 100-200 px/m at the defaults, 117-221 px/m
with `--bake-res 4096`.

**Bake** (`export_bake.bake`, `denoise`): each atlas is baked as one joined temporary copy while the
originals are hidden from the render, margin `EXTEND` res/128 px. All lights of the scene count,
including the `obj['fill']` lights of rooms that have no fittings yet. **Cycles does not denoise
bakes in 5.1.1** (`scene.cycles.use_denoising` changes nothing, measured), so the atlas is denoised
with OpenImageDenoise through a compositor Denoise node (CPU, 0.2 s per 1024 px). Normal maps are
part of the baked shading. Sunlit outside faces of ceiling slabs sit in the room atlases (blue
patches in the JPEG): unseen, harmless.

**Probes** (`export_bake.probe_point`, `render_probe`): one per house.json room at floor + 1.5 m,
at the grid point (0.2 m) with the largest mean free distance over 16 horizontal directions + up
and at least 0.2 m clear of everything, so it stays out of furniture and chandeliers. 1024 x 512,
everything visible.

**GLB** (`export.export_glb`, `compress`, `check_glb`): Blender exporter with extras, then
glTF-Transform `resize` (max 2048), `webp` on base-colour / emissive textures only (quality 88),
`meshopt --quantize-texcoord 14`. Deliberately no `optimize`, `dedup`, `prune`, `join`, `instance`,
`simplify`, `palette`: they drop the unused-looking `TEXCOORD_1`, merge named nodes or lose the
extras. `check_glb` then asserts on the raw and the compressed file that every lightmapped object
is a named mesh node whose primitives all have `TEXCOORD_1`, that extras survived and that no
lights / cameras were exported.

**Visual check** — re-imports the uncompressed GLB into an empty scene, lights it with nothing but
`base colour x lightmap(UV2) x intensity` as emission and renders preview cameras:
```
"$B" -b --factory-startup --python blender/export_check.py -- [--assets docs/assets] [--glb build/export/home_raw.glb]
     [--out build/export/check] [--cams living:bay,hallway:front,...]
```
Compare `build/export/check/<room>_<cam>.jpg` with `build/preview/<room>_<cam>.jpg`. Blender cannot
import meshopt, hence the raw GLB (`build/export/home_raw.glb`, written by every export).

**For room modellers**
- Give an object `lm='dynamic'` in `ctx.add` when it moves or is too intricate to deserve atlas
  space; ornate static trim costs texels (the hall cornice alone is 2 900 islands).
- A `plan_sym` object's footprint includes all its parented children: parent the parts of one
  piece of furniture to the tagged root.
- Scale 1 on static objects (the texel density is computed from mesh-space areas).
