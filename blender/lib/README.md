# blender/lib — API reference for room modellers

Everything a `blender/rooms/<id>.py` module may call. Read with `blender/CONTRACT.md` and
`spec/BRIEF.md`. Units are **metres**, world coordinates: origin = centre of the inside face of the
street-door threshold, **+Y into the house, +X to the right walking in, Z up**, ground-floor FFL at Z = 0
(every other floor, the basement and the site carry their world Z: `ctx.floor_z(room)`). The multi-level and
exterior rules are in `blender/MULTILEVEL.md`.
Object scale is always 1. All of `blender/build.py` and `blender/lib/**` is owned by the integrator:
room modules never edit lib files — if something is missing, say so in your report.

| section | what |
|---|---|
| [Quick start](#quick-start) | template, single-room preview, cameras, restyling a wall |
| [build.py](#buildpy) | command line, stages, levels, previews, triangle report |
| [ctx](#ctx-libctxpy) | house.json accessors, levels, zones, roof, `ctx.add`, `opening_frame` |
| [shell](#shell-libshellpy) | what is already built, finishes, `repaint`, `box`, `wall_runs` |
| [lighting](#lighting-liblightingpy) | daylight, emitters for fittings, white balance |
| [preview](#preview-libpreviewpy) | cameras and renders |
| [materials](#materials-libmaterialspy-textures-in-blendertextures) | key list, `paint`, `uv_box` |
| [props](#props-libpropspy) | furniture parts, hardware, pictures, curtains, lamps, plants |
| [mouldings](#mouldings-libmouldingspy) | `MB` mesh builder, profiles, sweeps, room trim |
| [joinery](#joinery-libjoinerypy) | doors, windows, surrounds (already installed by the shell) |
| [interact](#interact-libinteractpy) | operable things: `IX.tag`, door groups, water / flame / clock / TV / curtain / cupboard helpers, `--pose 1` |
| [site](#site-libsitepy) | ground zones, steps, boundaries, gate, shed shell, neighbours |
| [envelope](#envelope-libenvelopepy) | facade skin, exterior reveals and sills, roof, roof windows, balcony |
| [export](#export-blenderexportpy-export_bakepy-export_checkpy) | per-level GLBs, lightmaps, probes, sky, manifest schema 2, footprints, budgets, hero stills |

## Quick start

1. Copy `blender/rooms/_template.py` to `blender/rooms/<module>.py`. The module is the room id or the pseudo-room
   id (`front side_passage garden shed`), except `landing1` (landing1_front / _ql / _rear), `landing2`
   (landing2_head / _platform), `eaves` (eaves_front / _rear) and `basement` (+ basement_stair): `ctx.module_of(room)`.
   Objects are always tagged with the real room id. Set `ROOM`, replace the body of `build(ctx)`.
2. Preview your room on the real shell, with your own tag so parallel runs do not overwrite each other:
   ```
   B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
   "$B" -b --factory-startup --python blender/build.py -- --only shell,living --preview living --res 540x960 --samples 64 --tag me
   ```
   → `build/preview/living_<camera>_me.jpg`, one per entry of your `CAMERAS`. Add `--cam bay` for a
   single camera, `--save build/me.blend` to keep the scene. The foundation build (`--only shell,site,envelope`) takes ~6 s,
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
- Budgets (all instances counted): 300 k triangles for living, dining, kitchen, green_bedroom, blue_bedroom,
  loft_office, garden, front; 150 k for other rooms; per level G 0.85 M, 1 1.3 M, 2 0.85 M, B 0.15 M, X 0.85 M.
  build.py prints the table (`[build] tris  G living ...`).
- A module that builds its own flight calls `shell.remove(<stairwell room>, 'flight')` first (the shell always
  builds a plain carcass). `rooms/stairs.py` does not yet, so two flights overlap there.

## build.py

Contract: `blender/MULTILEVEL.md` section 5.

```bash
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$B" -b --factory-startup --python blender/build.py -- [--house <path>] [--levels B,G,1,2,X] [--only <stage>,...]
    [--bare] [--save build/home.blend] [--preview <what>,...] [--res WxH] [--samples n] [--cam name]
    [--tag suffix] [--pose 0|1]
```
- `--house`: default `spec/house.json` (schema `house/2`).
- Stages, in order: `shell` (grid, pieces, flight carcasses, thresholds, then joinery and trim), `site`, `envelope`
  (`lib/site.py`, `lib/envelope.py`: skipped with one log line when the module does not exist; an exception is an
  error and the build goes on), then the room modules: house rooms in file order, then pseudo-rooms. A module that
  serves several rooms (`landing1`, `landing2`, `eaves`, `basement`) runs once.
- `--only`: stage names and room / pseudo-room ids; default everything. `--levels`: restricts every stage; `X` = site,
  envelope and the pseudo-room modules. `--bare`: no joinery, no trim, and missing material keys are not errors.
- Fill lights go to every kind `room` / `stairwell` room of the built levels that has no `kind='light'` object,
  and to the shed workshop until `rooms/shed.py` brings fittings.
- `--preview`: room ids (the module's `CAMERAS`, else `preview.default_cameras`), `level:<id>`, `plan:<level>`
  (`plan:X` = site), `section`, `elev:front|rear|flank`, `all`. Files: `build/preview/<room>_<cam>[_<tag>].jpg`,
  `plan_<level>[_<tag>].jpg`, `section[_<tag>].jpg`, `elev_<side>[_<tag>].jpg`. Previews render after `--save`.
- The log ends with the triangle report by level, room and kind against the budgets (over-budget lines are flagged,
  not fatal) and `BUILD OK`, or `BUILD FAILED: <errors>` with exit code 1. Errors: an exception in a stage, a room
  module, an opening or a room's trim; a missing material key; a dado top that differs between `mouldings.TRIM` and
  `shell.FINISHES`; more than 60 k shell triangles.

The foundation (no room modules), then the bare-shell test run:
```bash
"$B" -b --factory-startup --python blender/build.py -- --only shell,site,envelope --save build/foundation.blend \
    --preview plan:B,plan:G,plan:1,plan:2,plan:X,section,elev:front,elev:rear,elev:flank --res 720x960 --samples 48 --tag fnd
```
```bash
"$B" -b --factory-startup --python blender/build.py -- --only shell --bare \
    --preview plan:B,plan:G,plan:1,plan:2,section,level:1 --res 540x540 --samples 48 --tag core
```

- `--pose 1`: previews with every interaction-tagged object in state 1 (doors swung, drawers out, taps
  running, curtains closed — see [interact](#interact-libinteractpy)). Default 0 = as modelled, with
  the `show when=1` objects hidden. Only the previews are posed: `--save` always writes state 0.
- Imports inside modules: `from lib import ctx, shell, lighting, preview, materials, mouldings,
  joinery, props` (build.py puts `blender/` on `sys.path`).

## ctx (`lib/ctx.py`)

```python
ctx = House.load()                    # spec/house.json; build.py passes the same ctx to every stage
ctx.spec                              # the raw json dict (ctx.spec['ceilingDefault'], ['bounds'], ...)
ctx.rooms[id], ctx.walls[id], ctx.openings[id]      # dicts of the raw json entries by id
ctx.features                          # list of feature dicts;  ctx.feature(fid) -> one of them
ctx.stairs                            # list of flights / steps; ctx.stairs['rise'] still reads the main flight; ctx.stair(id)
ctx.room_poly(id) -> [(x, y), ...]    # inside wall faces, counter-clockwise (piers / breast NOT included)
ctx.floor_z(id), ctx.ceil_z(id)       # floorZ / HIGHEST ceiling of the room (world Z); with x, y: steps, zones, slopes
ctx.room_at(x, y) -> room id | None
ctx.col(name) -> Collection           # get/create: 'shell', 'room_<id>', 'lighting'
ctx.add(obj, room, kind, plan_sym=None, lm=None) -> obj
ctx.opening_frame(oid) -> dict
ctx.errors                            # list of failed stages (build.py)
```
**`ctx.add`** links `obj` **and all its parented children** into `room_<room>` (collection `shell`
when `kind == 'shell'`), unlinks them from any other collection and tags them:
- `obj['room']` (after `ctx.tag_room`), `obj['level']` (= `ctx.level(room)`), `obj['kind']` ∈ `shell trim joinery fit furn decor light` (child lamps of a prop are
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
| `z0` | floor level of the opening (`floorZ`: world Z on every level) |
| `wall_thickness` | of the wall in house.json |
| `face_pos`, `face_neg` | signed distance along `normal` from the centreline to the real wall faces: normally ±t/2; where a `reveal` sets the frame back (`d_back` −0.03, dining N openings +0.07) the face that is actually left |
| `room_pos`, `room_neg` | rooms on the +normal / −normal side |
| `swing_sign` | +1 leaf swings to +normal, −1 to −normal, 0 none |
| `virtual` | True for openings on virtual walls (nothing is cut) |
| `level`, `exterior`, `outward`, `face_out`, `ext_reveal`, `outside_room` | level id; exterior openings only: unit xy pointing out, signed distance centreline -> outer face, metres from the outer face to the outside of the frame (`extReveal`, else the rule of MULTILEVEL.md section 3), the `connects` end standing for outside |
| raw json | `type style surround hinge hingeAt openAngle transom connects notes ...` |

Example — a switch plate 0.15 m beside the living-room door on the living side:
```python
f = ctx.opening_frame('d_living')
n = f['normal'] * (1 if f['room_pos'] == 'living' else -1)          # wall normal into the living room
p = f['center'].xy + n * abs(f['face_pos']) - f['along'] * (f['width'] / 2 + 0.25)
sw = P.place(P.switch_plate(2), (p.x, p.y, 1.2), facing=tuple(n))
ctx.add(sw, 'living', 'fit')
```

### Multi-level API (`blender/MULTILEVEL.md` section 3)

`from lib import ctx as C; h = C.House.load(path=None)` — default `spec/house.json`; schema 1 or `"house/2"`.
The module imports without Blender (tests, tools): `opening_frame` then returns tuples instead of `Vector`; only
`col` and `add` need `bpy`. Contract: `blender/MULTILEVEL.md` section 3. Check: `python blender/test_ctx.py`
(also runs under `blender -b --factory-startup --python blender/test_ctx.py`), prints `CTX OK`.

| name | meaning |
|---|---|
| `C.PSEUDO_ROOMS`, `C.FRAME_D`, `C.MODULE_OF` | `('front','side_passage','garden','shed','facade','roof','neighbours')`; 0.06 m exterior frame depth; room -> module name |
| `h.spec`, `h.schema`, `h.features`, `h.grid` | raw json (never modified); 1 or 2; feature list; `lib.shell.Grid` after `shell.build` |
| `h.levels`, `h.level_info[id]` | `['B','G','1','2']`; `{id, name, datumZ, floors}` |
| `h.rooms`, `h.building_rooms` | the 28 house rooms; `shed_workshop`, `shed_store` (+ `'building'`) |
| `h.walls`, `h.openings` | house entries + building entries (copies with `'building'`, level `'X'`) |
| `h.stairs`, `h.stair(id)` | list of flights / steps (`h.stairs['rise']` still reads the main flight: phase-1 code); json + `treads: [dict(n, poly, z, riser)]` |
| `h.zones`, `h.zone(id)`, `h.zones_of(pseudo)`, `h.zone_at(x, y)`, `h.zone_z(id, x, y)`, `h.ground_z(x, y)` | site zones; `zones_of` / `zone_at` return ids; `zone_z` applies `fall`; `ground_z` lets step treads override |
| `h.tag_room(room)`, `h.level(room)`, `h.rooms_on(level)`, `h.kind(room)`, `h.is_exterior(room)`, `h.module_of(room)` | building room -> `'shed'`; `'B'|'G'|'1'|'2'|'X'`; ids in file order; `'room'|'stairwell'|'void'|'exterior'|'site'` (KeyError for unknown ids) |
| `h.room_poly(room, rect=False)`, `h.room_at(x, y, level=None)` | polygon; `rect=True` squares polygon-edge chamfers through `c` |
| `h.chamfers(room)` | `[dict(id, p, q, c, v, z, stop, reflex)]`: polygon-edge chamfers, then bay arris splays |
| `h.floor_z(room, x=None, y=None)`, `h.ceil_z(room, x=None, y=None)` | without x, y: floorZ / highest ceiling; with: steps, floor_step / zones, planes, roof underside |
| `h.roof_z(x, y, ground=False)`, `h.roof_plane(x, y)`, `h.roof_under(x, y)`, `h.roof_slab_t(plane)` | upper envelope of the roof planes; 0.30 pitched, 0.24 flat |
| `h.exterior_openings(level=None)`, `h.facade_of(oid)`, `h.opening_frame(oid)` | frame keys as phase 1 plus `z0`, `level`, `exterior`, `outward`, `face_out`, `ext_reveal`, `outside_room` |
| `h.col(name)`, `h.add(obj, room, kind, plan_sym=None, lm=None)` | collection; tags `room` (after `tag_room`), `level`, `kind`, `lm` |
| `C.point_in_poly`, `C.poly_contains`, `C.poly_area`, `C.plane_z`, `C.clip_poly` | pure 2D helpers |

Deviations from the contract text: `roof_slab_t` measures only flat planes against the ceilings; reveals affect
openings of their own level only; `along` / `normal` are exact unit vectors; flight treads are cut with infinite riser
lines (a strip up to 5 cm behind a newel goes to the neighbouring tread).

## shell (`lib/shell.py`, `lib/stairs.py`)

`shell.build(ctx, levels=None, bare=False)` (`blender/MULTILEVEL.md` section 4; check: `blender -b --factory-startup
--python blender/test_shell.py`, `SHELL OK`), then `joinery.install_openings(ctx)` and
`mouldings.install_room_trim(ctx, room)` for every room.
One grid for the whole house: the envelope blocks are filled as mass (each storey from 0.15 below its lowest floor),
rooms, reveals, wells and openings are carved, and only faces between solid and a room void are emitted — nothing
faces the outside (the envelope owns it). `levels` builds a subset; `bare` skips joinery and trim. Needs the schema-2
house.

| object | content |
|---|---|
| `<room>.walls` | wall faces, liners of openings (white), ledges, risers between split floors (the upper floor's covering) |
| `<room>.floor` | mass tops at `ctx.floor_z(room, x, y)`: floor, `steps` treads, low side of a `floor_step` |
| `<room>.ceiling` (`part='ceiling'`) | mass undersides at `ctx.ceil_z(room, x, y)`; for `ceiling.planes` rooms the sloped faces with roof-window holes and liners. `under_roof` rooms (eaves) get none |
| `<room>.chamfer.<id>` | diagonal face of a polygon-edge chamfer, or a bay arris splay with its 45-to-90 stop |
| `<room>.haunch.<id>`, `<room>.arch_fill`, `<room>.vault_fill` | ceiling splay, arch infill (walls along X or Y), vestibule vault |
| `<first through room>.flight` (`part='flight'`) | `stairs.carcass`: treads, risers, raked soffit (0.12 below the pitch line), open sides |
| `<first room>.threshold.<oid>` | hardwood bar where two floor finishes meet in a doorway |

Walls of rooms with sloped ceilings are clipped per grid cell to the ceiling plane (eaves: the roof slab underside).
Steps that sit on mass (main flight treads 13-14, the winders of the second flight) are left to the grid; the carcass
gives them only tread and riser faces. `stair_basement` is solid (`shell.SOLID_FLIGHTS`): treads and risers only.

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
- Stairs: a plain carcass per flight (`<stairwell>.flight`: treads, risers, raked soffit; `stair_basement` solid),
  the two-step sets cut into the upper floor, the wells and the skylight shaft. **Not built** (room modules
  `stairs`, `stairs2`, `basement`): strings, balustrades, newels, nosings, the spandrel panel on x 0.15 (until it
  exists the basement shaft shows from the hall), raking dado and skirting beside flights.
- Tile wainscot 1.20 on all four walls of the three bathrooms: repaint the shower walls with
  `porcelain_calacatta_slab`.
- **Not built anywhere** (room modules): kitchen and utility splashback tiles, the nook tiles and
  black soffit lining, the kitchen cornice notch round the hood chimney, brass door stops / cabin
  hooks, the lamb's-tongue chamfers on the living bay nibs.

**Finishes** — `shell.FINISHES[room]` (also `shell.finish(room)`):
```python
dict(upper='#..', lower='#..',      # wall finish above / below the dado split (equal when no dado)
     dado=0.965, dado_h=0.07,       # TOP of the dado rail ABOVE THE ROOM'S floorZ and its height; None = no dado
     ceiling='#..', joinery='#..',  # ceiling colour; colour of painted trim in this room
     faces=[dict(axis=0, at=0.80, mat='#9E6E60', range=(lo, hi)?, z=(z0, z1)?)],   # per-face overrides
     wainscot=(1.20, 'marble_metro') | None,       # tile on every wall face below z
     features={'wc_cistern_duct': 'marble_metro'})  # per-feature material
```
A material spec is `'#RRGGBB'` (matt paint) or a `lib.materials` key. `shell.split_z(room)` =
height where `lower` changes to `upper` (hidden behind the rail) or None.
Ground floor (every other room: read `shell.FINISHES`; unknown rooms get `DEFAULT_FINISH`):
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
shell.wall_runs(ctx, room, z=0.05) -> [loop, ...]       # z = WORLD Z; loop = [((ax, ay), (bx, by), kind, opening_id), ...]; runs may be diagonal
shell.remove(room, part)                                # e.g. ('stairs', 'flight') before a module builds its own flight
shell.faces_object(name, [(points, point the normal faces, spec), ...]) -> Object   # small non-axis pieces
shell.is_solid(ctx, x, y, z) -> bool                    # the grid at a point
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
  a picture rail 2.2 m above the floor: `for loop in shell.wall_runs(ctx, 'dining', ctx.floor_z('dining') + 2.2): ...` and sweep the
  `'wall'` runs.
- A missing material key logs `[shell] WARNING`, lands in `shell.MISSING`, renders grey and fails the build
  (unless `--bare`). `mouldings.TRIM[room]['dado']['top']` must equal `FINISHES[room]['dado']`.
- `stairs.carcass(ctx, stair_id, solid=None) -> Object`; `shell.section_cap(ctx, axis, at)` = black poche for previews.

**Known simplifications**
- `ponytail:` valleys inside the eaves are approximate (one roof plane per grid cell, taken at the cell centre).
- The squared-off corners behind the living-room chamfer and the stair-foot diagonal overlap inside the poche; both
  prisms hide it, and `wall_runs` substitutes the diagonal whatever the grid does between `p` and `q`.
- Soffits at winders are faceted, with a small vertical step at the newel.
- The bay gable slab would be lower than the green bedroom bay ceiling near the cheeks: the envelope leaves the slab
  hollow there (no underside below the top floor).

## lighting (`lib/lighting.py`)

`blender/MULTILEVEL.md` section 9. `lighting.setup(ctx, samples, res)` (called by build.py after the rooms are
built) = Cycles on all OptiX GPUs with the OptiX denoiser, AgX + look `Medium High Contrast`, plus daylight.

| name | value |
|---|---|
| `EXPOSURE`, view | -0.6 EV, AgX "Medium High Contrast" |
| `WHITE_BALANCE`, `WHITE_TINT` | 3000 K, -10: one balance indoors and outdoors (export multiplies it into atlases and probes) |
| `SUN_ELEVATION`, `SUN_AZIMUTH`, `SUN_DIR` | 24 deg, 28 deg east of the street normal, light travels (-0.429, 0.807, -0.407) |
| `SUN_STRENGTH`, `SUN_KELVIN`, `SUN_ANGLE` | 2.5 W/m2, 3600 K, 1.0 deg |
| `SKY_TINT`, `SKY_STRENGTH`, `SKY_ROTATION` | (1.0, 0.281, 0.073), 0.6, pi - azimuth: the sky that LIGHTS the scene |
| `SKY_SHOW`, `SKY_SHOW_TINT`, `GROUND_SHOW`, `WB_MATRIX` | 0.12, (1.0, 0.95, 0.85), (0.10, 0.11, 0.10), the measured 3000 K matrix: the sky the CAMERA sees |

The sky is `ShaderNodeTexSky` (first of `MULTIPLE_SCATTERING`, `SINGLE_SCATTERING`, `NISHITA` the build offers; disc
off, altitude 0, air / aerosol / ozone 1) x `SKY_TINT` -> Background x `SKY_STRENGTH`. Calibration (measured values
are recorded beside the constants; re-measure with `blender/test_shell.py -- --sky`): a horizontal white card in open
shade bakes to luminance 0.72 and, after the 3000 K balance, to (0.719, 0.718, 0.801), blue / red 1.11. That sky is
lamp-coloured (salmon when seen directly), so it is used for light only: camera rays (previews, stills, probes, the
viewer's `sky.jpg`) get the same sky texture taken back through the inverse balance x `SKY_SHOW_TINT` x `SKY_SHOW`,
which displays as a daylight sky, and `GROUND_SHOW` below the horizon (world shader, `Light Path > Is Camera Ray`).

- `lighting.setup(ctx, samples, res)` = `setup_cycles` (GPU, AgX, balance) + `setup_daylight` (sky, sun lamp, a
  Cycles portal 30 mm inside every `ctx.exterior_openings()` opening and under every roof window / roof opening).
- `lighting.setup_sky(tint=None, strength=None, rotation=None, display=True)`: the world alone; `display=False`
  leaves out the camera branch (measurements of the light sky).
- `lighting.downlight(ctx, room, x, y, z=None, watts=60, kelvin=2850, spot_deg=115, radius=0.035, name=None)`:
  default z = `ctx.ceil_z(room, x, y) - 0.015` (zones and slopes included). `bulb`, `strip` as in phase 1.
- `lighting.fill(ctx, room)`: only for kind `room` / `stairwell` rooms without fittings (build.py decides); lamps hang
  0.35 below `floor + min(room height, ceilingDefault)`, lowered to the ceiling over each lamp.

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
preview.render_plan(ctx, level, path, res, samples)                 # 'B' 'G' '1' '2', or 'X' = the site / roof plan
preview.render_section(ctx, path, res, samples, x=-0.25)
preview.render_elev(ctx, 'front'|'rear'|'flank', path, res, samples)
```
- `DEFAULT_CAMERAS` holds 2–6 cameras per room matched to the reference frames of
  `spec/rooms/<id>.md` §9 (e.g. hallway `inner front doorcase arch lobby rear`, living `bay tvwall
  north baycorner`, dining `entry east north south nw`); `ref` names the frame.
- `default_cameras(ctx, room)`: the reference-matched ground-floor set, else two eye-height views between the two
  polygon corners that are farthest apart. Pseudo-rooms need `CAMERAS` in their module.
- `render_plan(ctx, level, path, res, samples)`: top view cut at `plan_cut(ctx, level)` = 0.9 above the level's
  highest floor (B -1.41, G 0.9, 1 4.32, 2 7.39), cut mass in black. This is lower than the manifest's dollhouse
  `cutZ` (which runs above the door heads): at 0.9 doors and windows read as gaps, as in `spec/plan_*.png`.
  Level `X` = the whole site from above, uncut.
- `render_section(ctx, path, res, samples, x=-0.25)`: what lies east of the cut, **mirrored** so that +Y is on the
  right, as in `spec/plan_section.png` and `elev:flank`.
- `render_elev(ctx, 'front'|'rear'|'flank', path, res, samples)`: the view starts 5 / 5.5 / 0.85 m off the house
  (the west side is the party wall: use the `roof` aerial cameras).
- `camera`, `render`, `render_room` as in phase 1.
- `DEFAULT_CAMERAS` also holds the views of `front`, `side_passage`, `garden`, `shed`, `roof` (aerials), `stairs2`
  and the eaves (dark unless `--pose 1` opens the hatches) until their room modules bring `CAMERAS`.
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
`glass_obscure` (stipple nrm, 0.15 m) `glass_green` `glass_dark` `whisky` (decanter contents)
`water` (running tap stream, alpha 0.45).
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

### Phase-2 keys (site, envelope, upper floors)

Adds to the "materials" section of `README.md`. `M.mat(key)` resolves every finish / material key of
`blender/MULTILEVEL.md` section 8 (`M.SPEC_KEYS`, asserted by `blender/test_joinery.py` together with every material
the spec json names); all are one Principled BSDF with constants and image textures. Textures are synthesised by
`blender/textures/gen/phase2.py` (`python -I blender/textures/gen/make_all.py phase2`; no third-party content, no
reference pixels), 512 or 1024 px. Texture payload now 19 MB of the 90 MB budget.
`blender/textures/test_swatches.py --only <keys>` renders swatches and checks the GLB export (35 new keys: SWATCH OK).

| spec key | library key | repeat (m) | notes |
|---|---|---|---|
| `carpet_grey`, `carpet_grey_twist`, `carpet_pale`, `carpet_silver_beige` | same | 1.0 | #CFC9BC, #B9B4AB, #CFCAC3, #C9C2B3; share `carpet_mink_nrm`, sheen 0.3 |
| `chipboard` | `vinyl_grey_sheet` | 1.5 | eaves floors: grey sheet flooring over the boards (#8C8A85, eaves.md 4) |
| `porcelain_grey` | same | 1.81 x 0.91 | 300 x 600, long side along U, third bond (bathroom2) |
| `porcelain_pale` | same | 1.21 x 2.41 | 400 x 800, long side along V (green bathroom; also the en-suite) |
| `steel_chequer_plate` | same | 0.4 | five-bar tread plate, black paint (balcony deck) |
| `wood_effect_porcelain_plank_dark` | `wood_tile_floor_dark` | 1.22 x 3.61 | the ground-floor plank recoloured #7B6F5C (basement) |
| `marble_metro` | same (existing) | | 300 x 100 |
| `metro_carrara_100x400` | same | 0.80 x 0.61 | 400 x 100 half bond, with nrm + orm |
| `porcelain_calacatta_slab` | same | 1.2 | grey + ochre veins, 2 mm joint on the repeat edge, rough 0.06 |
| `asphalt`, `grass`, `soil_lavender` | same | 2.0, 2.0, 1.5 | |
| `concrete_setts_grey_buff` | same | 1.97 | tumbled 160 mm setts, three tones |
| `concrete_flags`, `concrete_or_flags` | `concrete_flags` | 1.82 x 1.22 | 900 x 600 flags |
| `sandstone_flags_grey` | same | 1.84 x 1.85 | riven 600 x 450 |
| `clay_block_paving_red_herringbone` | same | 0.8 | 200 x 100 pavers, 90-degree herringbone |
| `composite_deck_dark_brown`, `timber_box_dark` | same | 1.17 x 1.6, 0.96 x 1.6 | boards along V |
| `buff_brick`, `stock_brick_yellow`, `stock_brick_grey`, `red_brick` | same | 1.8 x 1.2 | stretcher bond, 75 mm courses along U; one shared normal map |
| `closeboard_brown`, `closeboard_grey_painted`, `ledged_braced_grey` | same | 1.2 x 1.6, 0.76 | boards along V (vertical on a fence under `uv_box`) |
| `white_masonry_paint`, `render_sandstone`, `plinth_black` | same (`CONST`) | 1.0 | #F2F2EE, #D2C596, #2A2A2C + the shared `_render` sand normal map |
| `slate`, `fibre_cement_slate` | same | 2.4 x 2.0 | 250 mm courses along U: **V must run up the slope** (uv_box puts V on world Y, wrong on the bay gables: give those slabs their own UVs) |
| `flat_felt` | same | 1.0 | |
| `roof_underside` | same | 1.2 | black felt between rafters at 0.4 m centres along V |

Also new: `paint_oxblood` (shed store doors; `mo.MATS['oxblood']`).

Conventions kept from phase 1: UVs come from `M.uv_box(obj)` (U horizontal, V = +Z on walls, +Y on floors) or
from `mo.MB` (metres, divided by `size_m` in `finish()`); plank / board / rafter direction is V, courses run along U
(`uv_box(obj, rotate=True)` turns a texture 90 degrees).

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
  18 mm panels, back and `shelves` (bookcase, wine rack, plate rack, the carcass behind a door that
  opens): every face seen through the front (sides, top, bottom, back, shelves) takes `inner`
  (default = `mat`), the outside and the front edges stay `mat`. Clear inside: w − 36 mm wide,
  d − 6 mm deep, from z = plinth + 18 mm to h − 18 mm.
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
P.tv_screen(w=1.88, h=1.07)                                          # the lit picture, see interact
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
                gather=.6, tassel=.30, seed=1, fold_res=6, tie_mat='rope_cream', tassel_mat='tassel_gold',
                hardware=True)
P.curtain_pair(width=1.8, height=2.4, mat='tartan_red', stack=.5, tieback=True, tie_from_top=1.4, gather=.6,
               hang='pole', depth=.06, tassel=.30, seed=1, fold_res=6, hang_mat=None, finial='ball',
               tie_mat='rope_cream', tassel_mat='tassel_gold', hardware=True, cloth=True, closed=False)
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
- Curtains that open and close (see [interact](#interact-libinteractpy)): `curtain_panel(...,
  hardware=False)` = cloth only (no tie rope, hook or tassel; a `tieback=None` drop never has any) to
  hang on a pole that is already there; `curtain_pair(cloth=False)` = pole / pelmet / track only,
  `curtain_pair(hardware=False)` = the two drops with their ties but nothing to hang from,
  `curtain_pair(hardware=False, closed=True)` = the two drops drawn straight across the span, lapping
  20 mm in the middle, no ties. All three share the origin, so they go at the same place.
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
P.mantel_clock(w=.32, d=.16, h=.37, style='slate', mat=None, dial_dia=None, hands=True)
P.mantel_clock_dial(w=.32, d=.16, h=.37, style='slate', dial_dia=None) -> (centre Vector, radius)   # local frame
P.vase(height=.3, dia=.16, kind='baluster', mat='ceramic_white', flowers=0,
       flower_colors=('#D9482B', '#E88A2E', '#E06A8A'), seed=0)
P.plate(dia=.27, mat='ceramic_white', height=.022)
P.human_ref(height=1.7, mat='skin_ref')                              # preview-only scale mannequin
```
- `mantel_clock`: `'slate'` = black architectural case (stepped plinth, green colonnettes, stepped
  top with low dome, cream dial in a brass bezel — dining mantel); `'bracket'` = wooden bracket
  clock (stepped top, brass carrying handle, square brass dial, silvered chapter ring — living
  bookcase: `mantel_clock(.26, .15, .30, 'bracket')`). Origin bottom centre, front -Y.
  `hands=False` leaves the dial bare for live `P.clock_hands`; `mantel_clock_dial` (same size
  arguments) gives where they go.
- `vase` kinds: `baluster urn bottle bowl cylinder planter`; `flowers=n` adds simple blooms.
- `plate`: lies flat, origin centre of the base; `rotation_euler = (pi/2, 0, pi/2)` stands it on
  edge across a rack (lift it by dia/2).
- All glass is single-surface `glass_clear` (alpha-blended in the library).

### Test
`blender -b --factory-startup --python blender/lib/props.py -- --out build/props [--res 1600x900]
[--samples 64] [--only A,B2,D]` builds every prop in five bays with a 1.7 m mannequin, renders
`build/props/props_<bay><n>.jpg` (A turnings / cabinetry / hardware, B wall-hung, C soft
furnishings, D lighting / ornaments / plants, E interaction parts; `--only none` skips rendering),
writes `build/props/tris.txt` (per-prop triangle table) and ends with `PROPS SHEET OK` (asserts:
scale 1, UVs, finite coords, mesh sharing, `bulb_points`, water V range, flame count, hand count).
Whole sheet: 104 k tris.

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

### Phase 2: world Z, chamfers, every room

Replaces the "Room trim" bullets of the "mouldings" section of `README.md`; the mesh builder `MB`, `sweep`, the
profile helpers, roses, corbels and `brass_rail` are unchanged. Checked by `blender/test_joinery.py` (`check_trim`).

```python
mo.room_loops(ctx, rooms, z, solids=(), clip=None) -> [[(x, y), ...], ...]     # interior on the LEFT
mo.trim_runs(ctx, rooms, z, cfg=None) -> [([(x, y), ...], closed), ...]
mo.install_room_trim(ctx, room_id) -> [objects]       # <room>.skirting | dado | cornice (+ EXTRAS), kind 'trim'
mo.TRIM[room][kind]                                   # dict or list of dicts, see below
mo.surround_of(o, room), mo.surround_reach(oid, sur, room), mo.architrave_key(oid, room)
```

- **`z` is WORLD Z** everywhere (`room_loops`, `trim_runs`, `_edge_keeps`). `rooms` are ids of ONE level.
- **What is a mass at z** (`_masses`): the features of those rooms whose world `z` range holds z (`pier`,
  `pilaster`, `chimney_breast`, `boxing`, `nib`; `recess` is a void inside its range and a mass outside; `soffit`
  above its z), the rooms' `ceilingZones` that lie below z, and walls of the same level that exist at z
  (`baseZ - 0.01 <= z <= baseZ + height`). **On a schema-2 spec only walls inside one room** (both `rooms` equal:
  the arch walls) count: room polygons are the clear space, and a centreline wall rectangle may overlap a polygon
  corner (it does at the landing chamfer). Arch / opening gaps are open below `floorZ + springing`.
- **Chamfers (Algorithm C).** The outline is built on `ctx.room_poly(room, rect=True)` and then, at a height
  inside a chamfer's `z`, its vertex `v` is replaced by `p`, `q` (`ctx.chamfers(room)`): the 45-degree walls
  (hall / stairs, living NW, landing) and the bay arris splays (living to 2.20, green bedroom to 5.72). So skirting
  returns round the three faces of a splay and the cornice above keeps the square corner. Diagonal edges carry no
  openings; `MB.sweep` mitres the 135-degree corners.
- **Open edges carry no trim** (`_edge_keeps`): an edge on a virtual wall of that level (balustrades, step lines,
  well edges), or with clear room space of the same level just beyond it (another room, or the rest of the room
  beyond a `clip`). This replaces most of the phase-1 `skip` boxes.
- **Openings**: only those of the same level; `sill`, head and transom are taken `+ floorZ`; a raised door
  (`d_loft`) cuts the trim down to its `floorZ`. A door side without a `surround` entry counts as
  `plain_architrave` (`surround_of`).
- **cfg keys** (`TRIM` entries and `trim_runs`): `profile`, `top` (dado: top of the rail above the room's own
  floor), `mat`, `rooms` (outline of several rooms), `zone` (cornice of one `ceilingZones` id, at that zone's z,
  clipped to its polygon), `solids` (boxes or polygons), `skip`, `only` (plan boxes), `clip`, `open_above`
  (set by `install_room_trim` to ceiling - cornice height: a lower ceiling zone whose step is shallower than the
  cornice is open, not a wall — no cornice across the hall where the ceiling drops 0.11 at y 8.13).
- **`install_room_trim`** works at any `floorZ`: skirting at `floor_z(room)`, dado at `floor + top`, cornice at
  `ceil_z(room)` or the zone's z. Rooms not in `ctx.rooms` are skipped.

#### `mo.TRIM` (values the shell's `FINISHES[room]['dado']` must equal)
| rooms | skirting | dado `top` | cornice |
|---|---|---|---|
| vestibule | `sk_vest` | `dado_hall` 0.965 | - |
| hallway | `sk_hall` | `dado_hall` 0.965 | `cornice_hall` twice: `rooms=('hallway','stairs')` at 2.95 (front hall, the diagonal, the bulkhead face x 0.15; not the stair flank, not the screen) and `zone='rear_hall'` at 2.84 (lobby west, rear corridor; not the arch wall) |
| living | `sk_living` | - | `cornice_living` |
| kitchen, utility | `only` boxes as phase 1 | - | `cornice_kitchen`, `cornice_utility` |
| wc | - | - | `cornice_wc` |
| dining | `sk_dining` dark | `dado_dining` 1.05 | `cornice_dining` (pelmet solid) |
| landing1_front, landing1_rear | `sk_hall` | `dado_landing` **0.975** | `cove_70` |
| landing1_ql | `sk_hall` | `dado_landing` **1.165** (level with the rear corridor's rail) | `cove_70` |
| green_bedroom | `sk_hall` | - | `cornice_green` |
| blue_bedroom | `sk_hall` | - | `cornice_blue` |
| yellow_room | `sk_hall` | - | `cove_70` |
| green_bathroom / blue_ensuite / bathroom2 | - | - | `cove_100` / `cove_60` / `cove_80` |
| landing2_head, landing2_platform | `sk_hall` | `dado_landing` **0.99** | `cove_100` |
| purple_room, study | `sk_hall` | - | `cove_120` |
| loft_office | `sk_loft` (150) | - | - (sloped ceilings) |

No entry (nothing in the room specs, or raking trim that belongs to the room modules): basement,
basement_stair, stairs, stairs2, eaves_front, eaves_rear, balcony.

#### New profiles
`cove_60|70|80|100|120` (plain plaster coves), `cornice_green` 100 x 120 and `cornice_blue` 130 x 130 (their
"small enriched band" is a row of beads, `mo.BEADS`, set out by `mo.cornice`), `dado_landing` 65 x 28,
`sk_loft` 150, architraves `arch_upper` 80, `arch_70`, `arch_100`, `arch_hatch`. `ARCH_BY_ROOM` covers the
upper rooms; `DOORCASE_ARCH` / `doorcase_arch(sur, room)` give the architrave width under each doorcase.
`MATS` gained `oxblood`.

#### For room modules (not built here)
Raking skirting / dado / strings beside the flights and the two-step sets (`PROFILES['dado_landing']`,
`PROFILES['sk_hall']` with a sloping path), the rail that caps the loft front knee wall and the panel mouldings of
the rear one, the roses of the green and blue bedrooms (`mo.ceiling_rose(style, name)`), bedroom pelmets, the
small run moulding at Z 2.60 over the hall cupboard, the cove on the north face of the landing downstand, the
lamb's-tongue stops (core's `<room>.chamfer.<id>` pieces).

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
- **Every leaf is interaction-tagged** (group = the leaf's object name, `blocks` = opening id) — see
  [interact](#interact-libinteractpy). Room modules do not tag doors.
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

### Phase 2: multi-level, exterior, shed

Replaces the "joinery" section of `README.md`; everything there still holds unless stated here.
Test: `blender -b --factory-startup --python blender/test_joinery.py -- [--house PATH] [--only id,id] [--pose 0|1]
[--render] [--res 420x560] [--samples 32] [--tag t]` prints `JOINERY OK`; `--render` writes
`build/joinery/<id>_<in|out>[_<tag>].jpg` (one wall slab per opening, both sides).

```python
from lib import joinery as J
J.install_openings(ctx)          # every opening of ctx.openings (house + shed); errors go to ctx.errors
J.build_opening(ctx, oid)        # one opening
J.validate(ctx) -> [str]         # unknown style / surround keys ([] on spec/house.json)
```

- **Heights** are measured from `fr['z0']` (the opening's `floorZ`); nothing assumes Z 0. A door with a sill
  (`d_loft`: 0.27 above the platform) is built from its threshold; on the low side its plain architrave runs on down
  to that room's floor.
- **Rooms and names.** Objects are named `<room>.<opening id>.<part>` and tagged with that room, where the room is a
  `connects` name, not necessarily the wall's room: `d_basement` gives `hallway.d_basement.*` and
  `basement_stair.d_basement.surround`. Joinery on the outside of an exterior opening belongs to the **inside**
  room (`blue_bedroom.d_balcony.leaf.0` swings onto the balcony); shed openings are `shed.<id>.*`, room `shed`
  (`ctx.tag_room`). Helpers: `J._room_names(fr)`, `J._inside(fr)`, `J._own(ctx, fr, room)`.
- **Exterior frames** are `ctx.FRAME_D` (0.06) deep and their outer face sits `fr['ext_reveal']` behind the outer
  wall face (`J._ext_depth`); the test asserts it within 4 mm. Exceptions, both marked `ponytail:` in the code and
  listed as spec requests: the ground-floor bay lights (15 mm behind the face: the shutters need the rest of the
  0.12 wall) and the WC window (25 mm behind the tiles, `flat_white_surround`). In the 40 mm shed partition the
  frame takes the 30 mm that is left.
- **Swing side** comes from `fr['swing_sign']` (never "the first room that is not outside"): `d_street`,
  `d_french`, `d_balcony`, `shed_d1`, `shed_store_doors` open outward, `d_back` inward.
  `hang_leaf(ctx, name, room, MA, px, t, hinge_x, angle, build, yA=-0.002, zb=FLOOR_GAP, upvc=False, h=1.97,
  hinges=True, blocks=True, label=None, swing=None, **props)`: `MA` = side frame of the side the leaf swings to,
  `yA` = y there of the leaf face on that side when shut; the hinge axis is 6 mm in front of that face.

#### Styles (`J.BUILDERS`, `J.builder_for`)
| style | builder | notes |
|---|---|---|
| `oak_4panel`, `oak_glazed` | `_door_internal` | as phase 1. A side with no `surround` entry still gets a plain architrave (`mo.surround_of`): the level-2 doors carry `surround: {}` |
| `pocket_oak` | `_door_pocket` | `J.POCKET_OPEN = {'d_wc'}` are modelled open (as filmed); every other one (`d_green_slide`) shut, state 1 slides it into the pocket |
| `mahogany_glazed_double` | `_door_mahogany` | unchanged |
| `white_glazed_double` | `_door_street` (`double_door`), `_door_french` (`french_door`) | both through `_upvc_doorset`: frame at `ext_reveal`, transom + fanlight when the hole is taller than the leaves. Street: 45 mm jambs (phase 1 had 4 mm skins), frosted transom without lettering, room-face flange. French: `d_french` (round cat flap, dining dark recess), `d_balcony` (two fanlights, dark-lined reveal) |
| `white_back_door` | `_door_back` | same door set, 45 mm jambs, opens into the kitchen |
| `shed_french` | `_door_french` | no fanlight, mid rail at 0.75..0.85, 70 mm threshold |
| `shed_oxblood_pair` | `_door_timber_pair` | 45 mm painted frame, two-panel leaves, turned knobs, material `oxblood` (= `paint_oxblood` #7A3B2E) |
| `white_flush_pair` (type `hatch`) | `_hatch` | the json hole is the OUTER size of the white frame (75 mm stiles, 50 mm rails, lining through the knee wall); two 18 mm lay-on leaves, brass knobs, 110 degrees into `swingInto` |
| `white_upvc_fixed`, `white_upvc_obscure`, `white_upvc_casement`, `white_upvc_two_light`, `white_upvc_obscure_top_hung`, `shed_window` | `_window_upvc` | see below |
| `dark_timber_white_upvc_shutters` | `_bay_window` | as phase 1, but each of the six shutter panels is its own object `<room>.<id>.shutter.<i>` |
| `plain_semicircular_arch`, `segmental_arch_corbels` | none | types `arch` / `opening` (`J.NO_JOINERY`): plaster only |

**Windows.** `transomBar` (above `floorZ`) puts a 50 mm transom; `lights` = columns (three lights share the width
0.27 / 0.46 / 0.27, as the green-bedroom bay); `sashes` names the opening lights: `all`, `lower` / `main`,
`upper` / `fanlight` / `fanlights`, `west` / `east` / `centre` (lower row), `lower_w` / `lower_e`, `centre_top`;
`type` `fixed` | `top_hung` | `side_hung` with `hinge` `west|east|south|north`; `angle` defaults 20 (top hung) / 45
(side hung); all swing out. Every non-fixed sash is its own object `<room>.<id>.sash.<n>` (+ `.glass`), 12 mm
proud of the frame outside, handle inside. `operated: false` leaves it untagged. The shed windows carry none of
this in the spec; `J.SHED_WINDOWS` supplies it from `shed.md` (shed_w1: two top-hung fanlights over one pane,
shed_w2: two fixed lights). `'obscure'` in the style name selects `glass_obscure`.

#### Surrounds (`J.SURROUNDS`, reach for the trim in `mo.surround_reach`)
- Existing: `plain_architrave`, `pediment`, `dark_architrave`, `dark_aedicule`, `mahogany_frame`,
  `white_upvc_frame`, `plaster_reveal`, `flat_white_surround`, `white_architrave_two_lights`, `dark_timber`.
- `J.doorcase(mb, hw, top, arch, aw, frieze, shelf, consoles, apex, rake, frieze_ornament, tympanum_ornament,
  volutes, band)` builds the upper-floor doorcases from `J.DOORCASES` (heights above the door head):
  `cornice_hood_on_consoles` (landing face of `d_green`: 80 architrave, frieze, 1.25 x 0.10 x 0.11 shelf on two
  acanthus consoles), `pediment_scrolled` (green bedroom, both doors: frieze relief, 0.36 consoles, 1.30 shelf,
  pediment to +0.62 with tympanum relief and volutes), `pediment_tall_plain` (bathroom face of the sliding door:
  egg band, long consoles, pediment to +0.75), `pediment_triangular` (blue bedroom: 70 architrave, shelf, open-bed
  pediment to +0.37 with a swag; the landing face of `d_blue` uses a 90 architrave, 1.03 shelf, apex +0.28).
- `dark_recess` (dining N windows) and `dark_screen` (`d_french`): `_dark_recess` lines the `reveal` feature the
  opening sits in — jamb and head boards, back panel, 0.10 reeded architrave with legs to the floor, and for the
  windows the window-seat board (top = recess floor, 30 mm nosing), apron and 60 mm plinth. On the phase-1 spec
  (one reveal across the wall) `dark_screen` still builds the old `_dark_screen`.
- `dark_timber_reveal` (`d_balcony`): dark boards on the jambs and head from the frame to the room face.

#### Interaction tags (INTERACT.md; room modules never tag these)
| part | tag | notes |
|---|---|---|
| door leaf (+ glass) | `hinge`, `blocks` = opening id, group = leaf name | shut leaves open `J.OPEN_DEG.get(id, 90)` (`d_balcony` 85, `shed_d1` 100, `shed_store_doors` 95); leaves modelled open carry `on` |
| pocket door | `slide`, `blocks` | `on` only for `POCKET_OPEN` |
| hatch leaf | `hinge` 110, label "Eaves hatch", **no** `blocks` (hatches are no portals) | prop `door` keeps it in the static lightmap |
| window sash (+ glass) | `hinge` about the head (top hung) or the hinge stile, label "Window", no `blocks` | prop `door` = opening id, so `export_bake.classify` keeps the shut sash static like a door leaf |
| bay shutter panel | `hinge` +-100 into the room, label "Shutter" | front panels hinge on the mullion between each pair, return panels on their room end, so open panels clear the bay corners and each other |

`LABEL`: `d_basement` 'Basement door' (the phase-1 `d_understairs` key stays for the schema-1 file), `d_balcony`,
`shed_d1`, `shed_store_doors` added.

#### Not built here
Velux and skylight (envelope, section 7), shower / sauna glass doors and their trays (room modules), hardwood sill
boards of the upstairs windows and the utility window board, pelmets, brass threshold strips (`shell._thresholds`),
door stops and cabin hooks, the louvre tilt of the shutters.

#### Measured (fixture, `test_joinery.py`)
47 openings, 78 k triangles of joinery; with the trim the whole house is 185 k in `build.py --only shell`.

## interact (`lib/interact.py`)

The contract is `blender/INTERACT.md` (types, params, what each kind of thing needs) — read it first.
Blender only **tags**; the viewer animates. This section is the lib side of it.

```python
from lib import interact as IX
IX.tag(obj, t, **kw) -> obj            # validates, writes obj['ix'] = '<json>'; g defaults to obj.name
IX.tag_many([objs], t, g=..., **kw)    # the same tag on everything that moves together (g required)
IX.pose(objs, state=1)                 # check renders: hinge / slide move in state 1, `show` objects follow `state`
```
- `t` and its required keys: `hinge` (`p`, `deg`; `a` default +Z), `slide` (`d`), `show` (`when`;
  `fx` `none water flame tv glow`), `trigger`, `clock` (`hand`, `p`, `a`), `light` (`rooms`), `lamp`.
  Optional on any: `g label on reach blocks dur`. A wrong / missing key raises `ValueError`.
- Points and vectors are **world** metres of the object as modelled. A prop is unlinked when you tag
  it, so take them from `obj.matrix_basis` (always current), not `matrix_world`:
  `p = obj.matrix_basis @ Vector(local_point)`, `a = obj.matrix_basis.to_3x3() @ Vector(local_axis)`.
- `deg` follows the right-hand rule about `a`. With `a = (0, 0, 1)` and a front that opens toward
  you: **hinge on your left → negative, hinge on your right → positive** (whatever way the unit
  faces). About the unit's local +X (`a = M3 @ (1, 0, 0)`): a top-hung flap lifts with `deg = -100`,
  a bottom-hung oven door drops with `deg = +85`.
- Tagged objects are their own objects, added with `ctx.add(..., lm='dynamic')`; tag before or after
  `ctx.add`, in any order.

**Check both states.** `build.py ... --preview <room> --pose 1 --tag me1` renders the previews with
every tagged object of the scene in state 1 (default `--pose 0`: as modelled, `show when=1` objects
hidden). Parents are cleared first, as the export does, so a child you forgot to tag stays behind
exactly as it will in the viewer. In a scratch script: `bpy.context.view_layer.update();
IX.pose([o for o in bpy.data.objects if 'ix' in o.keys()], 1)`.

### Doors (done by joinery — do not tag them again)
`joinery.install_openings` tags every leaf; the group id is the leaf's object name:

| group `g` | type | state 0 → 1 | label |
|---|---|---|---|
| `vestibule.d_street.leaf.0` / `.1` | hinge ∓90 | shut → open into the vestibule | Front door |
| `hallway.d_inner.leaf.0` (east) | hinge −90 | shut → open into the hall | Door |
| `hallway.d_inner.leaf.1` (west) | hinge −85, `on` | open → shut | Door |
| `living.d_living.leaf` | hinge −95, `on` | open → shut | Door |
| `hallway.d_understairs.leaf` | hinge −90 | shut → open into the hall | Cupboard door |
| `hallway.d_kitchen.leaf`, `utility.d_utility.leaf`, `dining.d_dining.leaf` | hinge ±90, `on` | open → shut | Door |
| `kitchen.d_back.leaf` | hinge +90 | shut → open into the kitchen | Back door |
| `dining.d_french.leaf.0` / `.1` | hinge ∓90 | shut → open outward | Garden door |
| `utility.d_wc.leaf` | slide (0.511, 0, 0), `on` | in its pocket → shut across the opening | Door |

- Members of a group: the leaf (`<g>`, with its handles, letter plate, hinges and cat flap in the
  same mesh) and `<g>.glass` where the leaf is glazed. `p` = the hinge axis at floor level (the
  leaf's origin), `a` = +Z, `blocks` = the opening id. Double doors: one group per leaf, both with
  the same `blocks`.
- A leaf modelled open (`openAngle` / `joinery.LEAF_ANGLE`) gets `on=True` and the `deg` that shuts
  it; a leaf modelled shut opens the way its `hinge` / swing says, by `joinery.OPEN_DEG.get(id, 90)`
  degrees — lower it there if furniture ends up in the swing. Labels: `joinery.LABEL`.
- Anything a room module fixes **to a leaf** (a hook, a sign) must join the leaf's group with the
  leaf's own parameters: `IX.tag(hook, **json.loads(leaf['ix']))`. Keep furniture out of
  the swept quarter-circles of both states (checked with the furnished house: nothing is hit now).

### Helpers in props
```python
P.cabinet_carcass(w, d, h, mat, open_front=True, shelves=n, inner='#F4F2EC')   # lined interior, see props
P.water_stream(height, dia=.012, splash=.06)
P.flame_ring(dia=.07, n=24, h=.014)
P.clock_hands(radius=.1, style='baton', mat='plastic_dark', second=None, name=None) -> (hour, minute[, second])
P.tv_screen(w=1.88, h=1.07)
P.curtain_panel(..., hardware=False)
P.curtain_pair(..., hardware=True, cloth=True, closed=False)
P.mantel_clock(..., hands=False);  P.mantel_clock_dial(w, d, h, style, dial_dia) -> (centre, radius)
```
- `water_stream`: thin round stream from the **origin (the spout outlet) straight down** to
  z = −`height`, necking to 60 % of `dia` over the first 0.15 m, plus a flat splash disc `splash`
  across just above the foot (`splash=0`: none). Material `water` (library key: alpha 0.45, blended,
  double-sided). UVs: U once round, **V along the fall** — 0 at the foot, +1 per 0.1 m up to the
  outlet; the disc carries on to negative V at its rim. 76 tris for 0.16 m.
- `flame_ring`: crown of `n` pointed flames on a circle `dia` across, `h` high, leaning outward.
  Origin: centre of the burner at the foot of the flames, +Z up — put it 1–2 mm above the burner
  cap; `dia` ≈ the cap diameter. Material `flame_blue` (dark blue base, emission `#3D6BFF` x 6,
  double-sided). UVs per flame: V 0 at the foot, 1 at the tip. 4 tris per flame.
- `clock_hands`: separate objects modelled **pointing at 12 (+Z) for a dial facing −Y**, origin at
  the dial centre **on the dial face** (hour 1.5–2.5 mm, minute 3–4 mm, second 4.5–5 mm in front of
  it). `radius` = dial radius: hour hand reaches 0.50, minute 0.80, second 0.85 of it. `style`:
  `'baton'` tapered bars | `'spade'` antique spade hour + lance minute hand | `'sweep'` batons + a
  red second hand; `second=True/False` overrides whether there is a second hand. Objects are named
  `<name>.hand_h|m|s`. 52–72 tris the set.
- `tv_screen`: one quad, 0..1 UVs (U to the viewer's right, V up), material `tv_screen` (black base,
  pale blue emission the viewer replaces with its animated picture). Origin centre, in the plane
  y = 0, facing −Y. For `tv_panel(w, h, depth, standoff, bezel)` make it `w − 2·bezel` x
  `h − 2·bezel` and put it at local y = −(`standoff` + `depth` + 0.0016), 1 mm proud of the glass.
- Curtains and `mantel_clock(hands=False)`: see the props section.

**Examples** (all run and rendered in both states by `build/lib_ix/readme_examples.py`):
```python
from mathutils import Vector
from lib import interact as IX, props as P

# cupboard on a wall whose room side is -Y, at (x, yw): lined carcass, door hinged on the left, handle on the right
c = P.place(P.cabinet_carcass(.6, .56, .87, 'navy_cabinet', open_front=True, shelves=1, inner='#F4F2EC',
                              name='kitchen.base.b1'), (x, yw, 0), facing=(0, -1))
d = P.place(P.panel_door(.597, .717, name='kitchen.base.b1.door'), (x, yw - .56, .15), facing=(0, -1))
h = P.place(P.handle_bar(vertical=True, name='kitchen.base.b1.pull'), (x + .245, yw - .58, .70), facing=(0, -1))
IX.tag_many([d, h], 'hinge', g='kitchen.base.b1', label='Cupboard', p=(x - .2985, yw - .56, 0), deg=-100)
ctx.add(c, 'kitchen', 'fit'); ctx.add(d, 'kitchen', 'fit', lm='dynamic'); ctx.add(h, 'kitchen', 'fit', lm='dynamic')

# tap: your own lever + spout; one stream from the spout outlet (sx, sy, sz) to the bowl 0.21 m below
ws = P.place(P.water_stream(.21, name='utility.tap.water'), (sx, sy, sz))
IX.tag(ws, 'show', g='utility.tap', when=1, fx='water')
IX.tag(lever, 'trigger', g='utility.tap', label='Tap')            # or 'hinge' with p / a / deg=20
ctx.add(ws, 'utility', 'fit', lm='dynamic')

# hob burner k: cap top at (bx, by, zc), cap 70 mm across
fl = P.place(P.flame_ring(.07, name='kitchen.hob.flame.%d' % k), (bx, by, zc + .002))
IX.tag(fl, 'show', g='kitchen.hob.%d' % k, when=1, fx='flame')
IX.tag(knob, 'trigger', g='kitchen.hob.%d' % k, label='Hob')
ctx.add(fl, 'kitchen', 'fit', lm='dynamic')

# mantel clock with live hands (any rotation of the clock)
ck = P.place(P.mantel_clock(hands=False, name='dining.clock'), (x, y, z), facing=(0, -1))
c0, r = P.mantel_clock_dial()                                     # same size arguments as mantel_clock
centre, out = ck.matrix_basis @ c0, ck.matrix_basis.to_3x3() @ Vector((0, -1, 0))
for hand, w in zip(P.clock_hands(r, 'spade', name='dining.clock'), 'hms'):
    hand.location, hand.rotation_euler = centre, ck.rotation_euler
    IX.tag(hand, 'clock', hand=w, p=centre, a=out)
    ctx.add(hand, 'dining', 'decor', lm='dynamic')
ctx.add(ck, 'dining', 'decor')

# TV on the wall x = 0.80 (room side +X): the set is the trigger, the picture shows in state 1
tv = P.place(P.tv_panel(1.45, .83, name='living.tv'), (0.80, 2.6, 1.35), facing=(1, 0))
pic = P.tv_screen(1.44, .82, name='living.tv.picture')
pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -.0716, 0)), tv.rotation_euler
IX.tag(tv, 'trigger', g='living.tv', label='TV'); IX.tag(pic, 'show', g='living.tv', when=1, fx='tv')
ctx.add(tv, 'living', 'fit', plan_sym='tv'); ctx.add(pic, 'living', 'fit', lm='dynamic')

# curtains: the pole stays, the tied-back pair is state 0, the closed pair state 1
kw = dict(width=1.9, height=2.45, mat='tartan_red', tie_from_top=1.35)
pole = P.curtain_pair(cloth=False, name='living.curtain.pole', **kw)
tied = P.curtain_pair(hardware=False, name='living.curtain.open', **kw)
shut = P.curtain_pair(hardware=False, closed=True, name='living.curtain.closed', **kw)
for o in (pole, tied, shut):
    ctx.add(P.place(o, (x, yw, 2.50), facing=(0, -1)), 'living', 'decor', lm='dynamic')
IX.tag(pole, 'trigger', g='living.curtain', label='Curtains')
IX.tag(tied, 'show', g='living.curtain', when=0, fx='none'); IX.tag(shut, 'show', g='living.curtain', when=1, fx='none')
```
A single extra drop on a pole that already exists: `P.curtain_panel(.9, 2.45, 'check_grey',
hardware=False)` (straight, cloth only).

## Review fixes (foundation review, 2026-11-19)

What the first review of the multi-level foundation changed, by module. Asserted in `blender/test_shell.py` /
`test_ctx.py` ("review fixes").

- **Spec (`spec/house.json`)**
  - Feature type **`ceiling_cove`** `{room, polygon, z: [springing, ceiling], sides: {east|west|north|south: reach}}`:
    quarter-elliptical vault from the listed walls of the polygon's bounding box up to the ceiling; neighbouring
    sides mitre, free ends are capped. Object `<room>.cove.<id>` (`ql_vault` over the quarter landing).
  - **`floor_void.bottom`** (default `z - 0.5`): depth of the cut. The up-facing face it leaves is wall paint, not the
    room's floor finish (`basement_shelf_w` -0.03, `basement_ledge_e` -0.50, `basement_strip_e`).
  - **`exterior.neighbours[].parts`** `[{polygon, top: Z | {c0, cx, cy}, covering, walls?}]` and **`front`**
    `{material, upper: {z, colour}}`: one prism per part (parts may overlap, the higher one shows); faces to the
    street take `front`, a part with `walls` takes that all round. `ctx.neighbour_top(nb, x, y) -> (z, part index)`
    is what the envelope cuts the party-wall skin against. `polygon` / `z` stay for the plan and the walk blockers.
  - `boxing` features `gbath_duct`, `bath2_pipe_boxing`; `extReveal` on nine upper-floor openings (inner reveal =
    wall - extReveal - `FRAME_D`); bay gable eave edges at the main gutter level 6.50 (apex 8.295); the side alley
    falls from -0.08, so there is no step at its mouth.
- **shell**: `planes` ceilings close the step between two planes that share an edge at different heights (inside the
  room polygon only); chamfer prisms split at the dado like the grid walls; a `SOLID_FLIGHTS` flight keeps its mass
  under the square treads; `_thresholds`: `THRESHOLD[oid]` (aluminium nosing at `d_basement`), `CARPET_STRIP` (brass)
  at every doorway of levels 1 and 2, none at doors to an exterior room.
- **lighting**: glossy rays see the display sky like camera rays (`setup_sky`); `void_fill(ctx, room)` puts 3 W bulbs in
  spaces that are only looked into (eaves, the shed store) until a room module gives them a fitting: `build.py` calls
  it, so they no longer bake black behind their doors.
- **envelope**: mitred sweeps (`_Mesh.rings`) for the bay cornice and the first-floor sill ledge, the bay transom runs
  light by light (no coplanar boxes); `PIER_PANELS` (sunk panels, cut out of the skin); gable struts lean outward at 60
  degrees to the bargeboards; `EDGE_TRIM` on fascia boards; gutters close on each other at a valley corner; the soil
  stack and every downpipe that reaches the ground are their own objects with **`plan_sym='pipe'`** (a blocking
  footprint; the plan draws the plain outline).
- **site**: neighbours from `parts`; shed kerbs and piers stand 5 mm proud of the walls, copings butt.
- **joinery**: uPVC door leaves stop under the frame head where there is no transom bar (`shed_d1`).
- **export**: `NONCOLOUR_MAX = 512` caps the `*_nrm` / `*_orm` maps in the GLBs (colour maps stay at 2048).

## site (`lib/site.py`)

Everything outside the house that is not its envelope, built from `ctx.spec['exterior']` (MULTILEVEL.md section 6).

```python
from lib import site
site.build(ctx) -> [objects]     # zones, steps, boundaries, side gate, shed shell, neighbours, backdrop
site.surface('deck') -> Object   # ground object of a zone (after build)
site.ZONE_MAT                    # zone `surface` -> lib.materials key
```

Check: `blender -b --factory-startup --python blender/test_site.py -- [--house PATH] [--cams a,b|none] [--pose 1]`
prints `SITE OK` and writes previews to `build/site/`.

### Objects (all level `X`, kind `shell`, `lm='static'` unless noted)

| name | what |
|---|---|
| `<room>.<zone id>` | zone slab: top at `ctx.zone_z` (a `fall` is cut into planar pieces), side faces only where the zone stands proud of what is beside it, down to 0.10 below that ground |
| `front.footway.kerb` | kerb stones in the road along the footway edge |
| `side_passage.kitchen_steps` | one flag (40 mm, 15 mm nosing on the open sides) on a riser block per `steps[].treads` |
| `garden.passage_step.drain` | channel drain, 0.13 wide, at the foot of the passage step |
| `front.front_wall_w`, `front.front_pier_w`, `.cap` | stretcher courses by texture, modelled soldier course with joints, cast-stone cap |
| `garden.<fence>`, `.posts`, `.trellis` | panels (boards by texture), capping, three arris rails, concrete posts and gravel boards, lattice topper on the bays beside the deck |
| `side_passage.side_gate` (kind `joinery`, `ix` hinge), `.frame` | ledged-and-braced leaf with hinge straps, lock and latch; goal-post frame |
| `shed.walls`, `.roof`, `.soffit`, `.workshop.walls / floor / ceiling`, `.store.walls / floor / ceiling` | the shed shell |
| `shed.heads`, `shed.roof.kerb`, `shed.fascia` (kind `trim`) | soldier courses over the openings; roof kerbs, corner piers and caps; fascia, gutter, downpipe, soffit vent |
| `neighbours.<id>`, `neighbours.<id>.yard`, `neighbours.west_neighbour_wall`, `neighbours.backdrop` | massing boxes, a yard between each and the street, the neighbour's extension, 60 x 80 m ground at Z -0.50 (`no_export`) |

### How it decides things

- **Gaps in the spec.** Plot area that no zone, house or building covers is found with a constrained Delaunay
  triangulation and added to the lowest zone that shares an edge with it; each is logged as `[site] spec gap`.
  `spec/house.json` has one left: under the front wall (0.81 m2, filled at footway level).
- **Shed.** The outline is solid mass; the rooms, the veranda zone (zones with `room == 'shed'`) up to
  `verandaSoffitZ` and the openings from `ctx.opening_frame` are carved out of it on a grid. A face takes its finish
  from the void it looks into (`SHED_FIN`, else the building's brick). An opening is carved through the whole wall
  from its `floorZ`; outside the frame plane (`ext_reveal`) the reveal is brick, inside it the room's wall finish.
- **Gate.** Leaf bottom = highest ground or tread under its sweep + 20 mm (-0.14); state 1 is
  `GATE_DEG` = 50 degrees towards `swingInto`. The hinge post stands 50 mm clear of the kitchen wall, so the pivot is
  0.155 m along the gate line from `hingeAt` and the leaf is 0.78 wide (spec 0.90: the line is only 0.94 long).
- **Fences.** Our side = the side inside the plot. A fence end within 0.3 m of a building is carried on to it; a
  fence starting at a gate end has no post there (the gate's latch post is).
- **Neighbour walls.** One that lies on a neighbour polygon is that massing box; otherwise a block `EXT_DEPTH` deep.

### Textures

`M.uv_box` world projection. Materials in `ROT` (deck and box boards, authored along V) are turned so the boards run
E-W on top and level on the sides, starting at the zone's corner. Brick registers to the base of the soldier course
(wall), the cap (pier) and the veranda paving (shed). Soldier bricks, rails, posts and caps are plain paint colours.
An unknown material key logs `[site] WARNING` once, renders grey and is listed in `site.MISSING`.

### Knobs

`THICK`, `ZONE_MAT`, `EDGE_MAT`, `ROT`, `KERB`, `DRAINS`, `FENCE` (rails side, trellis), `BAY`, `GATE_DEG`,
`SHED_FIN`, `SOFFIT`, `ROOF_FALL`, `EXT_DEPTH`, `EXPORT_BACKDROP` (True drops `no_export` from the backdrop).

### Not here

Cars, bins, flag, wall planters, fire pit, garden planters, trellis panels, lavender, furniture, condensers, the gully
and the inspection cover (room modules); shed doors and windows (joinery); shed lights, coving and skirting.

## envelope (`lib/envelope.py`)

```python
from lib import envelope
envelope.build(ctx)              # -> [objects]; needs only the step-0 ctx (no shell, no site)
envelope.roof_surface(x, y)      # outer roof Z (== ctx.roof_z), or None
```
Check: `blender -b --factory-startup --python blender/test_envelope.py -- [--no-render] [--only front,rear] [--with-site]`
prints `ENVELOPE OK`; renders go to `build/envelope/`.

### Objects

| name | room / kind | what |
|---|---|---|
| `facade.<facade id>` | facade / shell | skin faces on that facade + the four returns of each of its holes |
| `facade.returns` | facade / shell | skin on no facade (porch side, nib beside the bay, back addition south face) and the roof-step faces (dormer cheek, wall between the gable roof and the main eaves) |
| `facade.<facade id>.sills` | facade / trim | projecting sills; masonry transom and mullions of the ground-floor bay; the board under the French doors |
| `facade.front_A.trim`, `facade.front_B.kneeler` | facade / trim | pilasters, plinth, bay cornice, first-floor sill ledge, gable head rail and struts; brick kneeler |
| `facade.soil_stack`, `facade.pipes.<material>` | facade / fit | soil stack; downpipes, waste runs, a/c trunking (table `PIPES`) |
| `roof.<plane id>` | roof / shell | covering, fascias on free edges, soffit under overhangs, underside inside the roof voids |
| `roof.<eaves id or plane id>.gutter`, `roof.rear_fascia`, `roof.ridge` | roof / fit, trim | gutters, fascia board, ridge cappings |
| `roof.velux.frame`, `roof.velux.sash` | roof / fit, joinery | the sash is its own object with an `ix` hinge (top-hung, +30 degrees about +X), `lm='dynamic'` |
| `roof.skylight.kerb`, `roof.skylight.glass` | roof / fit | upstand and fixed glass over the stair |
| `roof.rear_chimney` | roof / shell | stack above the roof only |
| `balcony.floor`, `balcony.structure`, `balcony.rainpipe`, `balcony.lantern` | balcony / shell, fit | chequer plate at the room's `floorZ`; frame, railing, wall posts, struts; the lantern has no lamp and no `ix` yet |

### Rules the other stages can rely on

- **Skin** lies exactly on the envelope polygons, one face set per storey, from `zone min Z - 0.05` (lowest storey)
  up to the **roof surface** on the wall line. Hidden parts are not built: inside another prism, and the party side
  below the neighbour's roof. Under the porch the ground-floor wall runs up to the lean-to surface.
- **Holes** are `width x (sill .. top)` on the outer face for every `ctx.exterior_openings()` of the house; the
  returns sit 2 mm inside the hole and are `ext_reveal` deep, so the outside of a frame built at `ext_reveal` meets
  them. The bottom return of a door is a stone threshold strip 2 mm above `floorZ`.
- **Black plinth** on the rendered faces ends at `PLINTH_TOP = -0.08` (rear_elevation.md), not at 0.15.
- **Roof** = upper envelope of `roof.planes`; `ctx.roof_z` is the top everywhere. The underside (`roof_z -
  ctx.roof_slab_t`) exists only where it is at or above the top floor (the roof voids) and as a white soffit under
  overhangs: over the first-floor bay the slab is hollow, so nothing shows below the bay ceiling.
- Finish of a face that is on no facade = finish of the nearest facade (same facing counts 1 m nearer).
- Material keys used: `white_masonry_paint render_sandstone plinth_black stock_brick_grey red_brick slate
  fibre_cement_slate flat_felt roof_underside steel_chequer_plate upvc_white glass_clear`; any key `materials.mat`
  does not know falls back to a plain colour from `FALLBACK` / `exterior.colours`.

Not built here (room modules): canopy downlights, doorbell, socket, cameras, flag, condensers, taps, hose reel,
balcony planters and ivy, the lantern's lamp. Left out: lead flashings, the 45-degree splay and sunk panels of the
first-floor bay corners, the two curved gable braces.

## export (`blender/export.py`, `export_bake.py`, `export_check.py`, `export_fixture.py`)

`blender/MULTILEVEL.md` section 10. Turns a saved build
into everything the viewer loads. Driven only by the custom props `obj['room']`, `obj['level']`, `obj['lm']`,
`obj['kind']`, `obj['plan_sym']`, `obj['ix']`, `obj['no_export']`, never by object names.

```
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$B" -b --factory-startup build/home.blend --python blender/export.py -- --out docs/assets [--house spec/house.json]
     [--levels G,1] [--rooms a,b] [--bake-res 4096] [--samples 256] [--density 160] [--probe-res 1024]
     [--skip-bake] [--skip-off] [--tmp build/export] [--renders] [--stills-only] [--still-res 1920x1080]
```
| flag | meaning |
|---|---|
| `--house` | house json, schema 1 or 2 (default `spec/house.json`); copied to `<out>/house.json` without `notes` |
| `--levels G,1` | write only these level GLBs; without `--rooms` also bake only the rooms of these levels |
| `--rooms a,b` | bake / render only these rooms (house rooms and pseudo-rooms, e.g. `facade`); wins over `--levels` for baking. The others keep their entries from the existing `manifest.json`: only valid while their geometry is unchanged |
| `--bake-res` | upper bound of the atlas side (default 4096); the size itself follows the lit area, see below |
| `--samples` | Cycles samples for lightmaps and probes (default 256); hero stills use `max(256, samples)`, with `--stills-only` exactly `samples` |
| `--density` | lightmap texels per metre in house rooms (default 160); exterior rooms get half, `facade` / `roof` / `neighbours` a quarter |
| `--skip-bake` | no lightmaps or probes (old entries are kept): GLBs + manifest + footprints, about 30 s |
| `--skip-off` | no lights-off set; rooms rebaked in that run lose their off entries |
| `--tmp` | scratch directory (`<level>_raw.glb`, EXRs), default `build/export`: one per concurrent run |
| `--renders` | hero stills into `<out>/../renders` |
| `--stills-only` | only the hero stills (no bake, GLB or manifest); `--still-res 960x540 --samples 64` for framing tests |

Ends with `EXPORT OK`; exit 1 with a traceback or a `BUDGET FAILED` line otherwise. Needs `npx` (Node) for
glTF-Transform 4.5.1. One room module changed: `--rooms <room> --levels <its level>`.

**Order of work**: tags, lightmap UVs and atlas sizes, level GLBs, **budgets (before any bake)**, lightmaps, probes,
lights-off set, sky, manifest, stills, final budgets.

**Rooms and levels** (`retag`). The atlas key is `obj['room']`; a room that is neither a house room nor a
pseudo-room is exported as `neighbours` with a `WARNING` line (the phase-1 build has `shell`). The level of an
object is always the level of its room (`ctx.level`); a different `obj['level']` is corrected with a `WARNING`.
`check_ix` fails the export when one interaction group (`g`) has members on two levels (the viewer starts
interactions per level as each GLB arrives) or when a `light` / `lamp` tag names `facade`, `roof` or `neighbours`
(they have no lights-off atlas). Switches may name rooms of other levels.

**Output** (`<out>` = `docs/assets`)
| file | content |
|---|---|
| `glb/<level>.glb` | the objects of level B, G, 1, 2 or X, except `no_export`; a level without objects gets no file. +Y up; flat node list; node `extras` = the custom props (`ix` byte for byte); `TEXCOORD_0` tiling UVs, `TEXCOORD_1` lightmap UVs on lightmapped objects; no lights / cameras; meshopt + `KHR_mesh_quantization`, colour textures WebP, normal / ORM maps JPEG. Node names are unique across the files |
| `lightmaps/<room>.jpg` | one atlas per room (house rooms, `balcony`, `front`, `side_passage`, `garden`, `shed`, `facade`, `roof`, `neighbours`) |
| `probes/<room>.jpg` | equirect panorama per room of kind `room` / `stairwell` / `exterior` and per `front`, `side_passage`, `garden`, `shed` |
| `lightmaps_off/<room>.jpg`, `probes_off/<room>.jpg` | the same with every lamp and emissive off: same `TEXCOORD_1`, atlas at half the size, same probe positions. Every atlas except `facade`, `roof`, `neighbours`; every probe |
| `sky.jpg` | 2048 x 1024 equirect of the world alone, **as displayed** (view transform, look, exposure, white balance in the pixels), orientation of the probes |
| `manifest.json` | schema 2, below |
| `house.json` | the `--house` file without the `notes` fields |
| `footprints.json` | `[{name, room, level, plan_sym, obb [[x, y] x4], zmin, zmax, height}]` for every `plan_sym` object: minimum-area rectangle of its and its children's vertices in world XY; `level` = level of `room` |
| `../renders/<stem>.jpg`, `index.json` | Cycles stills, `[{file, room, level, title}]` |

Images under `glb/`, `lightmaps/`, `lightmaps_off/`, `probes/`, `probes_off/` that no manifest entry names any more
are deleted at the end of a run, and so is a schema-1 `home.glb`.

**manifest.json, schema 2**
- `levels [{id, name, datumZ, cutZ, rooms[], glb, bytes, triangles, nodes, interactive}]`: every level of the house
  plus `X` ("Outside", `datumZ` = lowest floor of its `rooms[]` entries, `cutZ` null). **`glb` is null** (bytes 0)
  for a level nothing is built on. `cutZ` = lowest `ceilingZ` of the level's kind-`room` rooms - 0.07.
- `loadOrder`: G, X, 1, 2, B, **only the levels that have a GLB**.
- `rooms [{id, level, kind, name, polygon, floorZ, ceilZ}]`: every house room, then `front`, `side_passage`,
  `garden`, `shed` (kind `site`, `ceilZ` null) with the largest walkable polygon tagged to them (zone or building
  room: forecourt, side_passage, deck, shed workshop). `facade`, `roof`, `neighbours` are only in `levels[X].rooms`.
- `lightmaps [{room, level, image, size, pxPerM, intensity, bytes, objects[]}]`, `lightmapsOff` (same shape, same
  `objects`), `probes [{room, level, image, pos [x, y, z], intensity, bytes}]`, `probesOff`.
- `viewpoints {room: {pos [x, y], look [x, y]}}` (first hero still of the room), `spawn {pos, yaw, level}`.
- `toneMapping`, `exposure` (2^EV of the view settings), `whiteBalance` (3x3 rows, for emissive colours).
- `sky {image, color, sunDir}`: `color` = mean displayed colour of the upper half of `sky.jpg`, `sunDir` = unit
  vector to the sun (x, y, z up), read from the scene's sun lamp.
- `firstView {bytes, files[]}`: `glb/G.glb`, the lightmaps and probes of the level-G rooms and the four json files
  (`plan.json` counts once the plan tool has written it). `encoding`: the text version of the next paragraph.

**Encoding of lightmaps and probes.** 8-bit sRGB JPEG, `linear = srgbDecode(pixel) * intensity`. `intensity` = 99.5th
percentile of the lit texels, at most 6 x the median of the texels brighter than 2 % of that percentile (`FLOOR`:
faintly lit cabinet backs do not count; exterior atlases, where sun and shade share one image, are capped by the
percentile only), with 1 LSB triangular dither. Lightmaps hold Cycles DIFFUSE
direct + indirect **without albedo** (radiance of a white surface): three.js wants `lightMapIntensity = PI *
intensity`, `texture.channel = 1`, `flipY = false`, sRGB colour space. Probes are plain radiance, image centre = +X,
increasing u turns towards -Y: the three.js equirect layout after the (x, z, -y) axis swap. The one white balance
of the scene view (3000 K, tint -10; matrix measured through Blender's display pipeline) is multiplied into every
atlas and probe, indoors and outdoors. `sky.jpg` is different: it is a display image, to be used as an sRGB
background without tone mapping.

**Atlas size** (`atlas_rule`, `export_bake.atlas_size`): the power of two nearest to the aimed texel density for
the lit area of the room, capped. Aim 160 px/m in house rooms, 80 in exterior rooms (`ctx.is_exterior`: balcony and
pseudo-rooms), 40 in `facade`, `roof`, `neighbours`. Cap = `min(--bake-res, 4096 house | 2048 exterior,
ATLAS_CAP[room])`. `ATLAS_CAP` in `export.py` is empty: add `{'hallway': 2048}` there when a budget fails.

**Budgets** (`budget`; all logged as `budget <what> <value> / <limit>`, any `OVER` exits 1):
- right after the GLBs, before any bake and also with `--skip-bake`: triangles per level (G 850 k, 1 1.3 M, 2 850 k,
  B 150 k, X 850 k) and in all (4.0 M); every GLB <= 40 MB, `glb/G.glb` <= 21.5 MB; the **first-view estimate**
  < 35 MB = `glb/G.glb` + json files + per level-G atlas the existing file (when it has the size about to be baked)
  or 2.7 MB x (size / 4096)^2 + per probe the existing file or 0.1 MB;
- at the end: largest file < 50 MB, real first view < 35 MB, `docs/` < 300 MB (the parent of `--out` when it holds
  `index.html`, else `--out` itself).

**What gets a lightmap** (`export_bake.classify`): `lm == 'static'` meshes, grouped by room; objects under 0.05 m2
or made only of metal / glass become `dynamic` (probe-lit, instancing kept); static linked duplicates are made
single-user; modifiers are applied first. Interaction tags: `hinge` / `slide` / `clock` objects and `show when=1`
objects become `dynamic`, except door leaves (`obj['door']` or a `blocks` tag) modelled closed. `show when=1`
objects are hidden from every bake, probe and still, exported visible, never a footprint. Leaves modelled standing
open (`on`) are hidden while baking. `check_glb` fails the export unless every tagged object is a named childless
root node of its level's GLB with the identical `ix` string and its geometry in place (1 mm).

**Lights-off set** (`export_bake.lights_off`, `bake_off`): all non-sun, non-portal lights hidden, every unlinked
emission strength zeroed. Indoors the off lightmap is the DIFFUSE bake plus an AO bake (1 m) times a cool ambient
term (`AMBIENT_OFF`, `AMBIENT_TINT`), `intensity` capped at `PEAK_OFF`; off probes get the same radiance added
uniformly. **Outdoors** (exterior rooms) nothing is added and nothing capped: sun and sky are still there, so the
off atlas is the on atlas minus the lamps.

**Lightmap UVs** (`export_bake.unwrap`): layer `Lightmap`, always the second one. Smart-project at 66 deg on welded
temporary copies, ring-shaped islands cut into strips, equal texel density, AABB packing with a gap of 1/512 of the
atlas. The layout does not depend on the bake resolution and is deterministic, which is what lets `--rooms` /
`--levels` re-export a GLB next to atlases baked earlier.

**Probes** (`export_bake.probe_point`): floor + 1.5 m, at the 0.2 m grid point with the largest mean free distance
(16 horizontal directions + up, capped at 4 m), at least 0.2 m clear of everything; on open ground the point
nearest the middle of the polygon. `void` rooms (eaves) get none. A room without a free spot is skipped with a log
line.

**Sky** (`export_bake.render_sky`): every object hidden, the world rendered through the scene's view settings with
the probes' panorama camera. Rendered in full runs and whenever `sky.jpg` is missing; kept in partial runs.

**Hero stills** (`heroes`): per room, the first of
1. `HEROES` of its room module, `blender/rooms/<module>.py`:
   `HEROES = [dict(name='bed', pos=(x, y, z), look=(x, y, z), title='Green bedroom - bed', fov_deg=80, room='green_bedroom')]`
   (landscape; `title`, `fov_deg`, `room` optional; a module that furnishes several rooms names `room`, else the
   camera belongs to the room it stands in);
2. its rows in the `HEROES` table of `export.py` (the hand-framed phase-1 ground floor);
3. the module's `CAMERAS` (the reference matches; fov capped at 90).
File `<room>_<name>.jpg`. Keep cameras >= 0.25 m clear of furniture.

**Checks**
```
# visual: re-import <tmp>/<level>_raw.glb, light it with nothing but base colour x lightmap(UV2) x intensity
"$B" -b --factory-startup --python blender/export_check.py -- [--assets docs/assets] [--level G] [--tmp build/export]
     [--cams living:bay,...] [--off] [--out <tmp>/check]
# structural, plain Python + PIL: manifest against the files it names
python blender/export_fixture.py --check docs/assets
# dry run of the whole chain before publishing (never into docs/): small atlases, then plan and viewer on that folder
"$B" -b --factory-startup build/home.blend --python blender/export.py -- \
     --out build/export_int --tmp build/export_int_tmp --samples 128 --bake-res 1024
python blender/export_fixture.py --check build/export_int                    # EXPORT CHECK OK
python tools/plan/draft.py --footprints build/export_int/footprints.json --out build/export_int
python tools/plan/check.py --assets build/export_int
node docs/test/e2e.mjs --assets build/export_int                             # ALL CHECKS PASSED
```
(`export_fixture.py` without `--check` built the pre-integration fixture from the phase-1 `build/home.blend`; that
mode is history.)
`export_check.py` without `--cams` renders one landscape view per lightmapped room of the level from its probe
position (`<room>_probe.jpg`); it also asserts that every node of the GLB carries that level. Blender cannot import
meshopt, hence the raw GLB.

Measured on the integration build (foundation + the eight phase-1 room modules: 1143 nodes, 827 k triangles, 2 x RTX
4090, 128 spp, atlases <= 1024): 7 min 50 s in all; five GLBs 50 s (G 21.2 MB, X 7.2, 1 4.6, 2 3.0, B 0.5), 35 atlases
about 4 s each, 30 probes 3 s each, the off set 4 min; first view 24.1 MB, 136 files, 46 MB.

**For room modellers**
- Give an object `lm='dynamic'` in `ctx.add` when it moves or is too intricate to deserve atlas space.
- A `plan_sym` object's footprint includes all its parented children.
- Scale 1 on static objects (the texel density is computed from mesh-space areas).
- Everything of one interaction group is tagged with rooms of one level.
