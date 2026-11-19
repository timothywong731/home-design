# Multi-level + exterior foundation — binding design contract

> **Status (integration, 2026-11-19).** Step 0 and the seven owners have landed and were integrated on a real build.
> `spec/house.json` IS the schema-2 spec (section 2 is history: the fixture, `adopt_house2.py`, `house.next.json` and
> `validate_house_next.py` are gone; `spec/validate_house.py` is the schema-2 validator and draws `spec/plan_*.png`).
> Changes made to this contract at integration are marked **[integration]**: the sky (section 9, question 17.1), the
> plinth (section 7), lightmap encoding (section 10), incremental interactions (11.3, question 17.2).
> **[review]** The first review added: feature type `ceiling_cove`, `floor_void.bottom`, `exterior.neighbours[].parts` /
> `front` with `ctx.neighbour_top`, the plan symbol `pipe` (blocks), thresholds by level / opening, the bay gable at the
> main gutter level (eave edge 6.50, apex 8.295, cheek-line roof 6.78 instead of the 6.18 of section 7) and the alley
> falling from -0.08 (no step at its mouth; route 7 of section 16). Details: "Review fixes" in `blender/lib/README.md`.

Read with `spec/BRIEF.md` (Phase 2), `blender/CONTRACT.md` and `blender/INTERACT.md`. Where this file differs from
CONTRACT.md, this file wins; INTERACT.md is unchanged. After one short sequential step (**step 0**, section 2) seven
agents implement it in parallel: **(a) core, (b) site, (c) envelope, (d) joinery / mouldings / materials, (e) export,
(f) plan, (g) viewer**. Section 12 lists files, signatures, fixtures and acceptance per agent. Nobody edits a file
they do not own; requests go in the final report. **No agent runs a git command that changes state** (BRIEF).

## 1. Vocabulary, tags, names

- **Level**: `B`, `G`, `1`, `2` (house.json `levels`) and `X` (everything outside the house rooms). Split floors are
  different `floorZ` inside one level. All Z are world Z (ground-floor FFL = 0).
- **Room id** = id in `house.json rooms` (28). **Pseudo-rooms** (`PSEUDO_ROOMS`, level `X`, kind `site`, not in
  `rooms`):

| pseudo-room | holds | built by | has polygon / probe / manifest `rooms[]` entry |
|---|---|---|---|
| `front` | zones forecourt, forecourt_alley_mouth, footway, road; front wall + pier; (cars, bins, flag: room module) | site | yes (forecourt) |
| `side_passage` | zones side_passage, side_alley; kitchen steps; side gate | site | yes (side_passage) |
| `garden` | zones deck, deck_step_n/e, lawn, lavender_bed, garden_path; fences; (fire pit, planters, trellis: room module) | site | yes (deck) |
| `shed` | shed shell, veranda, workshop + store interiors, shed doors and windows | site, joinery | yes (shed_workshop) |
| `facade` | outer skin of every house wall, exterior sills / reveals, soil stack, downpipes | envelope | no |
| `roof` | roof slabs, fascias, gutters, bargeboards, chimney stack, porch lean-to, roof windows | envelope | no |
| `neighbours` | neighbour massing, neighbour walls, backdrop ground | site | no |

  `balcony` is a real room (level `1`, kind `exterior`); its steel structure is built by envelope and tagged
  `room='balcony'`. The shed's rooms `shed_workshop` / `shed_store` are **building rooms**: geometry ids only; every
  object in or on the shed is tagged `room='shed'` (`ctx.tag_room`).
- **Exterior room** (one predicate, used by export densities and caps and by the viewer's probe choice):
  `ctx.is_exterior(room)` = `ctx.kind(room) in ('exterior', 'site')`, i.e. the balcony and every pseudo-room.
- **Object props** (set by `ctx.add`, never by hand): `room` (after `ctx.tag_room`), `level` (= `ctx.level(room)`),
  `kind`, `lm`, optional `plan_sym`, `part`, `ix`, `door`, `no_export`. **`level` is the level of the object's
  room**: balcony objects are level `1`, everything tagged with a pseudo-room is `X`.
- **Names**: `<room>.<what>[.<n>]` with `<room>` = the tagged room; shell surfaces `<room>.walls | floor | ceiling |
  flight | chamfer.<id> | haunch.<id>`; site `<pseudo>.<zone or boundary id>[.<part>]`, `neighbours.<id>`; envelope
  `facade.<facade id>[.<part>]`, `roof.<plane id>`, `roof.<eaves id>.gutter`. Names are unique across the scene; the
  viewer resolves manifest object lists across all level GLBs by name.
- **Room modules**: `blender/rooms/<module>.py`, module = room id or pseudo-room id, except `MODULE_OF =
  {landing1_front, landing1_ql, landing1_rear -> 'landing1'; landing2_head, landing2_platform -> 'landing2';
  eaves_front, eaves_rear -> 'eaves'; basement_stair -> 'basement'}` (matches `spec/rooms/*.md`). Objects are always
  tagged with the real room id. **Balustrades, newels, nosings and aprons on a virtual wall that bounds a stairwell
  room or a `floor_void`** (`v_balustrade`, `v_strip_well`, `v_platform_well`, `v_head_jog`, `v_head_nosing`) belong
  to that stairwell's module (`stairs`, `stairs2`, `basement`), not to the landing's.
- Walkable rooms: kind `room` and `exterior`. `stairwell` rooms are walked on their flight; `void` (eaves) rooms are
  looked into through hatches, never entered.

## 2. Spec adoption

### Step 0 (core, alone, before the other six start; plain Python plus one pure-data module)

1. `spec/adopt_house2.py`: reads `spec/house.next.json`, applies the gap fixes below, sets `"schema": "house/2"`,
   writes **`build/fixtures/house2.json`**. Straight risers are generated from `firstStraightRiserY`, `going` and
   `direction`; the script asserts that the result equals the literal arrays printed below.
2. `spec/validate_house2.py`: copy of `validate_house_next.py` plus checks for every gap field (riser count ==
   `risers`, riser orientation, `walk.ends` openings exist, every zone has `room`, shed walls have `rooms`, `fall`
   end points lie in their zone). Default input `build/fixtures/house2.json`, previews
   `build/fixtures/plan_<level|site|section>.png`.
3. `blender/lib/ctx.py`: the whole section-3 API. It is additive and keeps loading the schema-1 `spec/house.json`
   with unchanged behaviour, because the interaction workflow still builds from that file.

Every agent then builds and tests with `--house build/fixtures/house2.json` (Blender scripts and `draft.py`) or
`HOUSE=build/fixtures/house2.json` (node tests); the default of both stays `spec/house.json`. `spec/house.json`,
`spec/validate_house.py`, `spec/validate_house_next.py`, `spec/house.next.json` and `spec/plan_next_*.png` stay
untouched until integration. **At integration the orchestrator** (not an agent) copies the fixture to
`spec/house.json`, moves `validate_house2.py` to `validate_house.py` (default `spec/house.json`, previews
`spec/plan_<level>.png`) and deletes `house.next.json`, `validate_house_next.py`, `adopt_house2.py`,
`plan_preview.png` and `plan_next_*.png`.

### Gap fixes applied by `adopt_house2.py` (exact JSON; the result validates)

1. **Flights get `walk`** (plan footprint, ordered riser lines, end openings). Riser = `[[ax,ay],[bx,by]]` with the
   **far side (towards `toRoom`) on the left of a->b**; winder lines are also stored in `winders.risers`.
   ```json
   "stair_main": {"winders": {"risers": [{"n":1,"line":[[0.2,5.33],[0.65,5.05]],"ellipse":{"centre":[0.65,5.33],"semi":[0.53,0.28]}},
                                          {"n":2,"line":[[0.2,5.33],[0.8,5.2]]}, {"n":3,"line":[[0.2,5.33],[0.99,5.39]]}]},
     "walk": {"polygon": [[0.15,5.05],[0.65,5.05],[0.99,5.39],[0.99,8.13],[0.15,8.13]],
       "risers": [[[0.2,5.33],[0.65,5.05]], [[0.2,5.33],[0.8,5.2]], [[0.2,5.33],[0.99,5.39]],
                  [[0.15,5.6],[0.99,5.6]], [[0.15,5.83],[0.99,5.83]], [[0.15,6.06],[0.99,6.06]], [[0.15,6.29],[0.99,6.29]],
                  [[0.15,6.52],[0.99,6.52]], [[0.15,6.75],[0.99,6.75]], [[0.15,6.98],[0.99,6.98]], [[0.15,7.21],[0.99,7.21]],
                  [[0.15,7.44],[0.99,7.44]], [[0.15,7.67],[0.99,7.67]], [[0.15,7.9],[0.99,7.9]], [[0.15,8.13],[0.99,8.13]]],
       "ends": [{"room":"hallway","opening":"o_stair_foot"}, {"room":"landing1_ql","opening":"o_ql_main"}]}},
   "stair_basement": {"winders": {"risers": [{"n":10,"line":[[1.25,6.0],[0.265,5.19]]}, {"n":11,"line":[[1.25,6.0],[1.25,5.19]]}]},
     "walk": {"polygon": [[0.265,5.19],[1.25,5.19],[1.25,6.0],[0.93,6.0],[0.93,7.6],[0.265,7.6]],
       "risers": [[[0.93,7.6],[0.265,7.6]], [[0.93,7.4],[0.265,7.4]], [[0.93,7.2],[0.265,7.2]], [[0.93,7.0],[0.265,7.0]],
                  [[0.93,6.8],[0.265,6.8]], [[0.93,6.6],[0.265,6.6]], [[0.93,6.4],[0.265,6.4]], [[0.93,6.2],[0.265,6.2]],
                  [[0.93,6.0],[0.265,6.0]], [[1.25,6.0],[0.265,5.19]], [[1.25,6.0],[1.25,5.19]]],
       "ends": [{"room":"hallway","opening":"d_basement"}, {"room":"basement","opening":"o_basement_foot"}]}},
   "stair_second": {"winders": {"risers": [{"n":11,"line":[[0.2,8.13],[0.99,8.59]]}, {"n":12,"line":[[0.2,8.13],[0.55,8.73]]},
                                            {"n":13,"line":[[0.15,8.13],[0.15,8.73]]}]},
     "walk": {"polygon": [[0.15,6.06],[0.99,6.06],[0.99,8.73],[0.15,8.73]],
       "risers": [[[0.15,6.06],[0.99,6.06]], [[0.15,6.29],[0.99,6.29]], [[0.15,6.52],[0.99,6.52]], [[0.15,6.75],[0.99,6.75]],
                  [[0.15,6.98],[0.99,6.98]], [[0.15,7.21],[0.99,7.21]], [[0.15,7.44],[0.99,7.44]], [[0.15,7.67],[0.99,7.67]],
                  [[0.15,7.9],[0.99,7.9]], [[0.15,8.13],[0.99,8.13]],
                  [[0.2,8.13],[0.99,8.59]], [[0.2,8.13],[0.55,8.73]], [[0.15,8.13],[0.15,8.73]]],
       "ends": [{"room":"landing1_front","opening":"o_stairs2_foot"}, {"room":"landing2_head","opening":"o_stairs2_head"}]}}
   ```
   15 / 11 / 13 risers. (R11 / R12 of `stair_second` are kites at 30 / 60 degrees about the turning newel — an
   assumption; replace from `spec/rooms/stairs2.md` if it gives lines.)
2. **Head of the second flight**: `walls.v_head_nosing` gets `"roomsBelow": ["stairs2"]`; new opening
   `{"id":"o_stairs2_head","level":"2","wall":"v_head_nosing","type":"opening","center":[0.15,8.43],"width":0.6,"height":2.3,"sill":0,"floorZ":6.02,"connects":["landing2_head","stairs2"],"hinge":"none","swingInto":null,"style":null,"transom":null,"surround":{}}`.
3. **Zones** get `"room"`: forecourt, forecourt_alley_mouth, footway, road -> `front`; side_alley, side_passage ->
   `side_passage`; garden_path, deck, deck_step_n, deck_step_e, lawn, lavender_bed -> `garden`; shed_veranda ->
   `shed`. `road` and `lavender_bed` get `"walk": false` (default true). **Boundaries** get `"room"`: front_wall_w,
   front_pier_w -> `front`; west_fence, east_fence -> `garden`; side_gate -> `side_passage`; west_neighbour_wall,
   alley_neighbour_wall -> `neighbours`.
4. `side_alley.polygon` -> `[[4.53,0.74],[5.43,0.74],[5.43,9.6],[4.9,9.88],[4.5,9.03],[4.53,9.03]]` (it stopped 0.85
   short of the gate, so the gate led nowhere).
5. **`zFar` is replaced by `fall`** (the direction of "far" was undefined): forecourt `"fall": {"from": [1.9,-0.12],
   "to": [1.9,-5.2], "z": [-0.06,-0.14]}`; side_alley `"fall": {"from": [4.98,0.74], "to": [4.98,9.6], "z":
   [-0.20,-0.30]}`. Surface Z at p = `z[0] + t * (z[1] - z[0])`, `t = clamp(dot(p - from, to - from) / |to - from|^2,
   0, 1)`. `zone.z` stays (= `z[0]`, used for labels). Site, plan, export and the viewer all use this one formula.
6. `features.stairwell_void_2` gets `"top": 8.62` and `"room": "stairs2"`; `stairwell_void_1` gets `"room": "stairs2"`
   (the well over the winders is in no room polygon).
7. `hallway.ceilingZones` += `{"id":"lobby_under_flight","polygon":[[0.15,7.68],[0.99,7.68],[0.99,8.13],[0.15,8.13]],"z":2.3}`
   (the lobby under treads 13-15 of the main flight; without it the hall void runs through the treads).
8. **Shed** (`exterior.buildings[0]`): `"room": "shed"`; rooms get `"walk"` (workshop true, store false); walls get
   `"level": "X"` and `"rooms"` (left, right of a->b): shed_w_front `["shed_workshop","outside"]`, shed_w_rear
   `["outside","shed_workshop"]`, shed_w_west `["outside","shed_workshop"]`, shed_w_east `["shed_workshop","outside"]`,
   shed_w_store `["shed_store","outside"]`; each opening gets `"level":"X"`, `"connects"`
   (`["outside","shed_workshop"]` for shed_d1, `["shed_workshop","outside"]` for shed_w1 / shed_w2,
   `["outside","shed_store"]` for shed_store_doors), `"style"` (`shed_french`, `shed_window`, `shed_window`,
   `shed_oxblood_pair`), `"hinge"` (`both` / `none`), `"swingInto"` (`"outside"` / null), `"transom": null`,
   `"surround": {}`, doors also `"openAngle": 0, "outsideZone": "shed_veranda"`.
9. Optional per exterior opening: `"extReveal"` (metres from the outer wall face to the outside of the frame); the
   default rule is in section 3. The existing `w_ensuite.revealDepth` is read by that rule.

**[integration] Further spec fixes applied at adoption** (requests of the site, envelope and joinery owners):
`extReveal` 0.015 on `w_bay_front` / `w_bay_cheek_e` (the shutters need the rest of the 0.12 m wall) and 0.215 on
`w_wc` (frame 25 mm behind the tiles); `forecourt_alley_mouth` extended over the paving beside the bay (x 4.15..4.53,
y -0.12..0.74) and given the fall `{from [4.98,-0.12], to [4.98,-5.2], z [-0.08,-0.14]}`; `lavender_bed` starts at
y 20.5 beside the deck step; `east_fence` ends at the shed corner (4.45, 23.4); new boundary `alley_neighbour_gate`
(fence, (4.9, 9.88) -> (5.43, 9.6), room `neighbours`) closes the alley beside our gate; `eaves_rear` starts at
x 1.35, the dormer cheek line (it reached 0.10 under the flat stair dormer).

Derivations that need no new field: the facade of an opening = the `exterior.facades[]` entry listing its id; outer
wall face = wall centreline + thickness / 2 on the side whose `rooms` entry is `outside`; zone surface Z = `fall` or
`zones[].z` (first containing zone, smallest area first; `steps[].treads` override); stair tread level k = `fromZ +- k
* rise`; `steps` treads = strips between consecutive `riserLines`, inside `toRoom`; level of a building room = `X`.

## 3. ctx API (core, step 0, `blender/lib/ctx.py`)

Everything of CONTRACT.md stays. Additions (pure data unless noted):

```python
House.load(path=None)                      # default spec/house.json; schema 1 or 2; ctx.spec is the raw json
PSEUDO_ROOMS = ('front', 'side_passage', 'garden', 'shed', 'facade', 'roof', 'neighbours')
FRAME_D = 0.06                             # depth of an exterior frame (joinery builds to it)
ctx.levels -> ['B','G','1','2']            ctx.level_info[id] -> {id, name, datumZ, floors}
ctx.rooms                                  # the 28 house rooms only
ctx.building_rooms[id] -> room json + 'building'     # shed_workshop, shed_store
ctx.tag_room(room) -> room                 # building room -> its building's `room` ('shed'); else unchanged
ctx.level(room) -> 'B'|'G'|'1'|'2'|'X'     # rooms[room]['level'], else 'X'
ctx.rooms_on(level) -> [ids]               # file order; 'X' -> PSEUDO_ROOMS
ctx.kind(room) -> 'room'|'stairwell'|'void'|'exterior'|'site'    # pseudo-rooms and building rooms: 'site'
ctx.is_exterior(room) -> bool              # kind in ('exterior', 'site')
ctx.module_of(room) -> module name         # section 1
ctx.room_poly(room, rect=False)            # rect=True: polygon-edge chamfers squared off (through c)
ctx.chamfers(room) -> [dict(id, p, q, c, v, z=(z0, z1), stop=None|(z1, z2), reflex=bool)]
ctx.floor_z(room, x=None, y=None)          # floorZ; with x, y: floor_step low side and `steps` treads
ctx.ceil_z(room, x=None, y=None)           # no x, y: ceilingZ = HIGHEST ceiling of the room (as today);
                                           # with x, y: min(ceilingZ, ceilingZones, ceiling.planes) there;
                                           # under_roof rooms: roof_under(x, y)
ctx.roof_z(x, y, ground=False) -> z|None   # max of the roof planes containing (x, y); ground=True: porch only
ctx.roof_slab_t(plane_id) -> metres        # section 7: 0.30 pitched planes, 0.24 rear_flat / stair_dormer
ctx.roof_under(x, y) -> z|None             # roof_z - roof_slab_t of that plane (underside of the slab)
ctx.stair(id) -> dict                      # the json + 'treads': [dict(n, poly, z)] from walk.risers; ctx.stairs = list
ctx.zone(id) / ctx.zones_of(pseudo) / ctx.zone_at(x, y) / ctx.zone_z(id, x, y)     # zone_z applies `fall`
ctx.openings                               # house openings + building openings (level 'X', key 'building')
ctx.walls                                  # likewise (building walls carry rooms, level 'X', baseZ)
ctx.exterior_openings(level=None) -> [ids] # an end of `connects` is 'outside' or a kind-'exterior' room
ctx.facade_of(oid) -> facade dict | None
ctx.opening_frame(oid)                     # as today, with: z0 = o['floorZ'] (fallback: the room floor);
                                           # + level, exterior (bool), outward (unit xy, exterior only),
                                           # face_out (signed distance centreline -> outer face), ext_reveal,
                                           # outside_room (the connects end standing for outside, or None)
ctx.add(obj, room, kind, plan_sym=None, lm=None)   # room = tag_room(room); + obj['level'];
                                                   # collection 'shell' (kind 'shell') | 'room_<room>'
```
- `floor_z` / `ceil_z` without coordinates keep their phase-1 meaning, so existing room code keeps working; both
  (and `room_poly`, `kind`, `level`) also accept building-room ids. For `under_roof` rooms the spec `offset` (-0.31)
  is superseded by the slab underside (1 cm higher), so wall tops and slab meet with no crack.
- `opening_frame` on upper floors is identical in shape: `center.z = floorZ + sill`.
- **Connects end that is not one of the wall's rooms** (`d_balcony`: connects `blue_bedroom`, `balcony`; wall rooms
  `outside`, `blue_bedroom`): a kind-`exterior` room stands for the wall side whose room is `outside`. `swing_sign`,
  `outward` and `face_out` use that side, so `swingInto: "balcony"` swings outward. `room_pos` / `room_neg` stay the
  wall's rooms.
- **`ext_reveal`** = `o.extReveal` if given; else `t - o.revealDepth - FRAME_D` if `revealDepth` is given; else
  `min(default, d - FRAME_D)` with default 0.10 for windows, 0.08 for doors and d = distance from the outer face to
  the room-side face after `reveal` features (`abs(face_out - face_pos|face_neg)`). The result is clamped to >= 0.01.
  Examples: dining north windows (0.38 recess in the 0.50 wall, d = 0.12) -> 0.06; `w_ensuite` -> 0.01.
- **`ctx.chamfers(room)`** returns two kinds, same shape:
  - polygon-edge chamfers (features of type `chamfer`; a polygon edge p->q that is not axis-aligned): `c` = whichever
    of (p.x, q.y), (q.x, p.y) lies strictly outside the polygon, `v = c`, `z` = the feature's `z`, `reflex=False`;
  - bay arris splays (one per `bay.chamfers[]` item, id `<bay id>.<i>`): k = `corner` (a reflex polygon vertex), p and
    q = k moved `width / sqrt(2)` along each of the two polygon edges meeting at k, `c = p + q - k` (inside the
    wall), `v = k`, `z` = item `z`, `stop` = item `stop`, `reflex=True`. Living: 0.106 legs at (1.1, 0.99) and
    (4.0, 0.99), z 0..2.2, stop to 2.4; green bedroom: 0.085 legs at (1.16, 0.99), (3.9, 0.99), z 3.42..5.72, stop
    to 5.82. This is the owner's "45 at the bottom, 90 at the top".

**Algorithm C (chamfer substitution)**, used by `shell.wall_runs`, `mouldings.room_loops` and the plan: build the
rectilinear outline (it passes through `v`), then at a height inside the chamfer's `z` replace vertex `v` by the pair
p, q in loop order, i.e. the two runs through `v` become three: up to p, the diagonal p->q, on from q. Between `z[1]`
and `stop[1]` and above, the outline keeps the square corner.

## 4. Shell (core: `shell.py`, new `lib/stairs.py`)

One grid for the whole house (`ctx.grid`), built in this order. Tags as today (`feat:<id>`, `op|<oid>|<room>`, room
ids for voids), plus `mass`.

1. **Mass**: fill every `exterior.envelope.blocks[].levels[]` polygon from `min(z0, floorZ of every room of that
   level whose polygon overlaps it) - 0.15` to `z1`. Every storey therefore carries its own slab under every floor,
   including the split floors (`landing1_ql` 2.85 and `landing1_rear` 3.04 lie in the main block whose level 1 starts
   at 3.42), so floors exist for any `--levels` subset and under the ground-floor rooms outside the basement
   footprint. Rooms are carved after all mass, so the overlap between storeys never eats a room. Walls, floor zones
   between storeys, unseen zones and poche are simply what is never carved. `wall_rect` stays as a helper but no
   longer creates solids.
2. **Rooms** (not kind `exterior`: the balcony is outside the mass): carve `room_poly(rect=True)` from `floorZ` to
   `ceilingZ`; inside a `ceilingZones` polygon only to that `z`. Stairwell rooms are carved from `floorZ` to
   `min(ceilingZ, floorZ of the first `through` room of the `above` flight)`: `basement_stair` -2.1..0, `stairs`
   0..3.17, `stairs2` 3.42..8.62. Rooms with `ceiling.type` planes / under_roof: add the plane polygon coordinates to
   the grid, carve to `ceilingZ`, then (step 9) drop the box top and clip the wall quads.
3. **Inner walls** (`rooms[0] == rooms[1]`): fill `wall_rect` over `baseZ .. baseZ + height`.
4. **Features** as today, with world Z from `z`: pier, pilaster, chimney_breast, boxing, hearth (fill); recess, reveal
   (carve); arch_vault; `poche` needs nothing; `floor_step`: carve the low side `zLow..zHigh`; `floor_void`: cut solid
   over the polygon from `z - 0.5` to `top` (default `z + 0.02`), void tag = its `room`; `roof_opening`: cut from the
   room ceiling to `ctx.roof_z`; `bay` with `chamfers`: carve the square k..c from `z[0]` to `stop[1]`, void tag = the
   room (pieces in step 9). No feature id is special-cased any more (`lobby_overhead_cupboard` is an ordinary boxing).
5. **Steps** (`kind: steps`): cut each tread strip from its tread Z up to the `toRoom` floor. The riser faces between
   split floors come out of the grid as wall faces: they are real risers. This cut is the only geometry of a `steps`
   set (see 10).
6. **Flight sweeps**: for every tread of every flight, cut solid over (tread bounding rectangle ∩ W) from the tread Z
   to tread Z + 1.95, where W = the union of the flight's `through` room polygons and of the `floor_void` polygons
   whose `room` is in `through`. This opens the wall under tread 12 of the main flight, the first-floor slab over it
   and the well over the winders of the second flight; it does not touch a wall beside the flight: **walls a flight
   crosses are opened only by their openings** (`o_basement_foot` keeps its head at -0.46). Replaces the bespoke
   `_stairwell`; the pocket it carved behind the lobby cupboard flap is gone (hallway re-fit).
7. **Openings**: cut as today from `opening_frame`, through the full wall thickness to the outer face.
8. **Faces**: as today, except:
   - faces whose void side is outside are **not emitted** (the envelope owns the outside; `shell.exterior`,
     `shell.wall_tops`, `shell.ground` and `_add_ceilings` are gone);
   - up-facing faces of `mass` (and of step / `floor_step` cuts) under a void tagged with a room id are
     `<room>.floor`; down-facing faces of `mass` over such a void are `<room>.ceiling` (`part='ceiling'`);
   - faces of `feat:` solids keep `FINISHES[room]['features'][id]` or the wall finish, whatever their direction (the
     hearth top stays `hearth_marble`, the WC duct ledge stays tile); faces against an `op|...` void keep the white
     liner (sills, heads, jambs), as today.
   The floor-area self-check (`area > 0.85 x polygon`) skips kind-`stairwell` rooms and subtracts the `floor_void`
   polygons inside the room from the expected area.
9. **Non-axis pieces** (separate objects, kind `shell`, the room's finish):
   - `<room>.chamfer.<id>` for a polygon-edge chamfer: triangular prism p, c, q over the chamfer `z`: the diagonal
     face plus both end caps (the grid faces behind it are hidden inside it).
   - `<room>.chamfer.<id>` for a bay splay: prism p, c, q over `z[0]..z[1]` (visible face: the diagonal p-q) and,
     joined into the same object, the stop over `z[1]..stop[1]`: the prism p, c, q again plus the wedge whose sloped
     face is the triangle (p and q at `z[1]`, k at `stop[1]`), closed to the two wall planes.
   - `<room>.haunch.<id>`: `ceiling_haunch` = prism in the wall / ceiling corner at `wallAt`.
   - `<room>.ceiling` for `ceiling.type == 'planes'`: one face per plane polygon at `c0 + cx*x + cy*y`, with a
     rectangular hole and four liner faces up to `roof_z - 0.01` at every `roof_window` of the room. Wall quads of
     that room are clipped to `z <= ceil_z(room, x, y)` (per grid cell the ceiling is linear along a wall: one
     half-plane clip). `under_roof` rooms get **no** ceiling from core (the roof slab underside is their ceiling);
     their wall quads are clipped per cell at `ctx.roof_under` of the highest plane at the cell centre —
     `ponytail:` valleys inside the eaves are approximate.
   - Arches and the vestibule vault: `_curved` as today, generalised to arch walls along Y and to `floorZ` offsets
     (`springing` / `crown` are above the opening's `floorZ`).
10. **Stairs carcass** (`lib/stairs.py`, called by `shell.build`): `stairs.carcass(ctx, stair_id) -> Object` for
    **`kind: flight` only**: treads, risers and the raked soffit from `ctx.stair(id)['treads']`; object `<first
    through room>.flight`, `part='flight'`, tread material = the stairwell's `covering` / floor material, soffit =
    ceiling paint. `solid=True` for `stair_basement` (mass down to the shaft floor). It is always built; a room module
    that models its own flight calls `shell.remove(room, 'flight')` first. Strings, balustrades, newels, handrails,
    nosings, carpet detail (also on `steps` sets): room modules (ownership: section 1).
11. `_thresholds` (object `<first room>.threshold.<oid>`, tagged with that room, never `'shell'`), then `_install`
    (joinery + trim) as today.

`shell.wall_runs(ctx, room, z=0.05)` keeps its signature and meaning; runs may now be diagonal (kind `'wall'`,
Algorithm C; the grid outline passes through `c` for both kinds of chamfer) and `z` is **world Z**. New:
`shell.remove(room, part)`, `shell.build(ctx, levels=None)` (subset of levels while iterating: mass, rooms, openings
and stairs of those levels only).

**Finishes**: `FINISHES` (core) gets an entry for every room, from the surfaces section of `spec/rooms/<id>.md`
(**section 3 in the phase-1 room specs, section 4 "Surfaces & colours" in the new ones**); `dado` / `wainscot` /
`faces.z` are **above the room's floorZ**. Core may use only `'#hex'` paints and the finish keys listed in section 8.
Unknown room -> `DEFAULT_FINISH` (white, no dado). A missing material key logs `[shell] WARNING` and falls back to
grey paint; it counts as an error unless `--bare`. build.py asserts `mouldings.TRIM[room]['dado']['top'] ==
FINISHES[room]['dado']` wherever both exist. Ground-floor geometry changes arrive with the spec; the ground-floor
**room modules are not touched** here and will not fit until their agents re-fit them.

## 5. build.py (core)

```
blender -b --factory-startup --python blender/build.py -- [--levels B,G,1,2,X] [--only <stage>,...]
    [--bare] [--save build/home.blend] [--preview <what>,...] [--res WxH] [--samples n] [--cam name]
    [--tag suffix] [--pose 0|1] [--house <path>]
```
- Stages, in build order: `shell` (grid, pieces, carcasses, joinery, trim), `site`, `envelope`, then room modules
  (house rooms in file order, then pseudo-rooms). `--only` takes the three stage names and room / pseudo-room ids (a
  room id runs its module once; no pseudo-room is called `site`, so the names never collide); default everything.
  `--levels` restricts all stages to those levels (`X` = site + envelope + pseudo-room modules). `--bare` skips
  joinery and trim installation (core's own test).
- `site.build(ctx)` and `envelope.build(ctx)` are called if the module exists (missing module = one log line, as
  `_install` does for joinery); an exception adds to `ctx.errors` and the build goes on.
- `--preview`: room ids (the module's `CAMERAS` or `preview.default_cameras`), `level:<id>` (all its rooms),
  `plan:<level>` (orthographic top view clipped at the level's cut height, section 10), `section` (orthographic cut at
  x = -0.25 looking east), `elev:front|rear|flank` (orthographic elevations), `all`. Files
  `build/preview/<what>_<cam>[_<tag>].jpg`.
- `report_tris()` groups by `obj['level']`, `obj['room']` and `obj['kind']` (not by collection: every kind-`shell`
  object shares one collection), prints each group and the total against the budgets, then `BUILD OK`.

**Budgets**: whole property <= 4.0 M triangles; per level G 0.85 M, 1 1.3 M, 2 0.85 M, B 0.15 M, X 0.85 M; per room
300 k (living, dining, kitchen, green_bedroom, blue_bedroom, loft_office, garden, front), 150 k others; kind `shell`
of the house rooms (grid, pieces, carcasses) <= 60 k; rooms `facade` + `roof` <= 150 k; kind `shell` of `front`,
`side_passage`, `garden`, `shed`, `neighbours` <= 100 k.

## 6. Site (agent b: new `blender/lib/site.py`)

`site.build(ctx)` builds, from `ctx.spec['exterior']` only:
- **Ground**: one object per zone, `<zone.room>.<zone id>`, top face at `ctx.zone_z(id, x, y)` (a zone with `fall` is
  one sloped plane), kind `shell`, `lm='static'`, at least 0.10 thick, real edges where a zone stands proud (deck
  0.15 fascia boards, deck steps as boxes, veranda paving). Zones abut without gaps; a lower zone runs under the edge
  of a higher one, and every zone that touches the house runs up to the envelope polygon.
- **Steps**: `steps[].treads` as stone slabs; single risers (`passage_step`, thresholds) are the zone edges
  themselves. The channel drain at the passage step.
- **Boundaries**: walls (brick courses by texture, soldier course, pier caps), fences (posts, boards, trellis topper),
  the side gate as its own object tagged `IX.tag(..., 'hinge', blocks='side_gate', deg=<+-50>)` (closed = state 0;
  sign by the right-hand rule so that the leaf turns west, into the passage). The
  posts stand on the paving (-0.30); the **leaf's bottom edge is at Z -0.14** (20 mm over `kitchen_steps` tread 2 at
  -0.16) and **state 1 is 50 degrees** into the side passage: past 52 degrees the leaf would sweep through tread 1.
  The 100 degrees of `garden.md` cannot be reached with the treads as specified.
- **Shed shell** (`room='shed'`): walls, openings, flat roof with veranda soffit, workshop and store interior faces
  (floor, walls, ceiling) from `buildings[0]`; holes from `ctx.opening_frame(<shed opening>)`. Doors and windows of
  the shed are joinery (agent d, styles of gap 8).
- **Neighbours and backdrop** (`room='neighbours'`): plain boxes for `neighbours[]` and neighbour walls, low-detail,
  no windows, no numbers; a 60 x 80 m backdrop ground at Z -0.50 with `no_export`.
- Public: `site.build(ctx)`, `site.surface(zone_id) -> Object`, `site.ZONE_MAT` (surface key -> `materials` key). Not
  here: cars, bins, flag, fire pit, planters, trellis, lavender, furniture, condensers (room modules `front.py`,
  `garden.py`, `shed.py`, later).
- Nothing may stand inside the envelope polygons or cross a door portal (section 11 walk rules).

## 7. Envelope (agent c: new `blender/lib/envelope.py`)

`envelope.build(ctx)` builds, from `exterior.envelope`, `exterior.facades`, `roof` and `ctx.opening_frame` only:
- **Skin**: for every envelope block level without `below_ground`, faces on the outer polygon edges over the level's
  `z` (party wall side west: none below the neighbour's roof), finish from the facade it lies on (`facades[].finish`,
  `exterior.colours`; the exposed stock-brick strip x -0.75..-0.50 on rear_R), with rectangular holes `width x
  (sill..top)` at `center` for the openings of that facade.
  - **Base**: the lowest skinned storey of each block starts at `min(surface Z of the zones and step treads touching
    that edge) - 0.05` (below 0: forecourt -0.14, side alley -0.30, side passage -0.30, deck -0.05), so no slit is
    left between the paving and the wall. The black plinth runs from there to Z -0.08 (**[integration]**: was 0.15;
    `rear_elevation.md` section 5 and the stills show the band ending below the door sills; `envelope.PLINTH_TOP`).
    Door holes start at the
    opening's `floorZ`, so the plinth under each external door is its threshold riser.
  - **Roof steps**: the skin also covers every vertical step of the roof's upper envelope: along each plane-polygon
    edge where the surface on the other side is lower, a face from the lower surface up to the higher one, in the
    finish of the facade below (dark grey panel on the `stair_dormer` cheek). That gives the dormer cheek at x 1.35
    (y 5.47..8.73), the back addition's south face at y 8.73 (x 1.35..3.40, Z 6.99..8.87) and the x 3.40 face at y
    8.73..9.33.
  - **Clip**: every skin face of every level is clipped to `z <=` the roof surface just outside it — the level-2
    gables under the main slopes, the level-1 bay cheeks and front under the bay gable (eaves 6.18), the porch front
    under the lean-to (3.22 at y -0.12).
- **Exterior reveals and sills**: for each exterior opening, four return faces from the outer face inward by
  `ext_reveal`, 2 mm inside the hole, facade finish (they cover the white interior liner the grid emits); projecting
  sill, head detail. Joinery puts the outside of the frame exactly at `ext_reveal` behind the outer face — both sides
  use that one number from `opening_frame`.
- **Roof**: each `roof.planes[]` as a slab of thickness `ctx.roof_slab_t(plane)` = `min(structure.thickness - 0.01,
  min over the plane polygon of (plane z - ceil_z of the kind-room room below) - 0.01)`: 0.30 for the pitched planes,
  **0.24 for `rear_flat` and `stair_dormer`** (underside 8.63, clear of the 8.62 ceilings and of the loft
  `lobby_flat` at 8.57). Top = covering, underside = felt / rafters, visible in the eaves. The surface is the **upper
  envelope** of the planes: the plane polygons overlap and are not cut at the valleys (bay gable against the main
  front slope), so cut every plane where another is higher (`bmesh.ops.bisect_plane` along the valley line). Holes
  for `roof_window` / `roof_opening` features, with frame, glass and (Velux) an `IX` hinge. Ridge tiles, verges,
  fascias and gutters from `roof.eaves`, bargeboards and struts of `roof.gable`, lead abutments, porch lean-to with
  its soffit, soil stack, downpipes.
- **`rear_chimney`**: its spec polygon overlaps the dining room corner and the neighbour. Build the **stack only
  above the roof** (Z from `roof_z` to 9.87, plan clipped to x <= -0.53, y >= 16.46); below the roof the pier is the
  brick finish strip on rear_R, not a solid.
- **Balcony** (`room='balcony'`): deck plate, channel frame, railing, posts, struts, lantern from the
  `balcony_structure` feature. The deck top is the room's `floorZ`.
- Public: `envelope.build(ctx)`, `envelope.roof_surface(x, y) -> z` (same value as `ctx.roof_z`).
- Constraint: the skin lies exactly on the envelope polygons; nothing of the envelope is inside a room. Slate, render
  and brick are textures, not geometry.

## 8. Joinery, mouldings, materials (agent d: `joinery.py`, `mouldings.py`, `materials.py`, textures)

- **Styles** (every `style` in the spec builds; `joinery.validate(ctx)` returns `[]`): existing ones, plus
  `white_upvc_two_light`, `white_upvc_obscure_top_hung`, `white_flush_pair` (type `hatch`), `white_glazed_double` on
  the balcony, `shed_french`, `shed_window`, `shed_oxblood_pair`; arches `plain_semicircular_arch` need no joinery.
  `transomBar`, `lights`, `sashes` are honoured: every sash that is not `fixed` is its own object with an `IX` hinge
  (`operated: false` -> no tag).
- **Surrounds**: existing, plus `cornice_hood_on_consoles`, `pediment_scrolled`, `pediment_tall_plain`,
  `pediment_triangular`, `dark_timber_reveal`, `dark_recess`; `surround_reach` covers them.
- All heights from `fr['z0']` (= opening `floorZ`); nothing assumes Z 0. Exterior frames are `ctx.FRAME_D` deep and
  sit at `fr['ext_reveal']` behind the outer face (section 7). The outward side of an exterior opening comes from
  `fr['outward']` / `fr['swing_sign']`, never from "the first room that is not `outside`" (`d_balcony` swings onto the
  balcony). Object names and tags use `ctx.tag_room(room)` (shed openings: `shed.<what>`, room `shed`). Door leaves
  keep the INTERACT rules (`blocks` = opening id). `LABEL`: the key `d_understairs` becomes `'d_basement': 'Basement
  door'`.
- **Mouldings**:
  - `room_loops` / `trim_runs` / `_edge_keeps` take **world Z**. They use only walls with `baseZ - 0.01 <= z <= baseZ
    + height` and only openings whose wall passes that test (today every wall of every level cuts every outline).
    Every opening height they compare with (`sill`, `height`, top, `transom.height`, `springing`) is taken `+
    o['floorZ']`. Features are filtered by their world `z` as today.
  - They follow chamfers by Algorithm C, both kinds: diagonal walls with correct mitres at the 135-degree corners,
    and the bay splays, where skirting returns round the three faces (wall, splay, wall) while trim above `z[1]`
    keeps the square corner. `sweep` paths may be diagonal.
  - `install_room_trim` works at any `floorZ` (`fz + top`). `TRIM` gets an entry for every room that has skirting /
    dado / cornice in `spec/rooms/<id>.md`, and the ground-floor entries (hard-coded boxes) are re-derived for the
    new geometry. Rooms with sloped ceilings get no cornice on sloped runs. Raking skirting / dado beside flights and
    steps: room modules.
- **Materials**: `M.mat(key)` resolves every key used by the spec (via `ALIAS`): floors `carpet_grey`,
  `carpet_grey_twist`, `carpet_pale`, `carpet_silver_beige`, `chipboard`, `porcelain_grey`, `porcelain_pale`,
  `steel_chequer_plate`, `wood_effect_porcelain_plank_dark`; **wall finishes for `FINISHES`** `marble_metro`
  (existing, 300 x 100: blue_ensuite, bathroom2), `metro_carrara_100x400` (green_bathroom), `porcelain_calacatta_slab`
  (shower walls of the three bathrooms) — every other wall and ceiling of the new rooms is a `'#hex'` paint; zones
  `asphalt`, `clay_block_paving_red_herringbone`, `composite_deck_dark_brown`, `concrete_flags`, `concrete_or_flags`,
  `concrete_setts_grey_buff`, `grass`, `sandstone_flags_grey`, `soil_lavender`, `timber_box_dark`; boundaries
  `buff_brick`, `closeboard_brown`, `closeboard_grey_painted`, `ledged_braced_grey`, `stock_brick_grey`,
  `stock_brick_yellow`, `red_brick`; facades `white_masonry_paint`, `render_sandstone`, `plinth_black`; roof `slate`,
  `fibre_cement_slate`, `flat_felt`, `roof_underside`. Image-textured Principled only, <= 2048 px, texture payload <=
  90 MB. Fittings (sauna timber, shower trays) are room-module materials, not part of this list.

## 9. Lighting (core: `lighting.py`, `preview.py`)

Same mood as phase 1: every lamp on, view = AgX "Medium High Contrast", `EXPOSURE = -0.6`, **one white balance for
everything, indoors and outdoors: `WHITE_BALANCE = 3000` K, `WHITE_TINT = -10`**, multiplied into every atlas and
probe at export as today. New constants:

| constant | value |
|---|---|
| `SUN_ELEVATION` | 24 degrees (the rear garden lies in the house's shadow and is sky-lit; a look decision with `SUN_AZIMUTH`) |
| `SUN_AZIMUTH` | 28 degrees east of the street normal: unit plan vector **to** the sun (0.469, -0.883) |
| `SUN_DIR` (light travels) | (-0.429, 0.807, -0.407) |
| `SUN_STRENGTH`, `SUN_KELVIN`, angle | 2.5 W/m2, 3600 K, 1.0 degree (strength and colour as phase 1) |
| world | `ShaderNodeTexSky`, `sky_type` = first available of `MULTIPLE_SCATTERING`, `SINGLE_SCATTERING`, `NISHITA` (read the enum), `sun_elevation` 24 degrees, sun disc **off**, altitude 0, air 1, aerosol / dust 1, ozone 1; its colour is multiplied by `SKY_TINT` before the Background node |
| `SKY_TINT` | start (1.0, 0.86, 0.74) (the phase-1 dusk tint); calibrated once so that a horizontal white card in open shade (sun lamp hidden), **after the 3000 K balance**, has blue / red between 1.00 and 1.25 |
| `SKY_STRENGTH` | Background strength, **[integration]** 0.6: the same card bakes to 0.72 +- 0.07 scene-linear luminance (the first target, 0.30, left the garden, the side passage and the shed near black beside the lamp-lit rooms) |
| `SKY_SHOW`, `SKY_SHOW_TINT`, `GROUND_SHOW` | **[integration]** what the **camera** sees instead of the lamp-coloured sky: the same sky texture taken back through the inverse of the balance matrix (`WB_MATRIX`), x tint (1.0, 0.95, 0.85) x 0.12, and a grey-green (0.10, 0.11, 0.10) below the horizon |

- A physical sky under a 3000 K balance renders saturated blue (the phase-1 finding recorded in `lighting.py`);
  `SKY_TINT` is what keeps the one balance usable outdoors. Calibrated: `SKY_TINT = (1.0, 0.281, 0.073)`, card after
  the balance (0.719, 0.718, 0.801), blue / red 1.11 (`blender/test_shell.py -- --sky` re-measures and asserts).
- **[integration] Two skies in one world.** That tint is a lamp-coloured sky: seen directly it is salmon at the
  horizon. It stays the LIGHT (every ray except camera rays), so open shade reads neutral under the one balance.
  Camera rays (previews, stills, probes, `sky.jpg`) get the display sky of the table instead, mixed in the world
  shader by `Light Path > Is Camera Ray` (`lighting.setup_sky(display=True)`). Nothing else changes: one balance, no
  second exterior balance, no split of joinery into facade objects.
- The sun lamp gives all direct light (the sky's disc is off); `sun_rotation` of the sky is set so the bright side
  faces the lamp and verified by a 64 px panorama (brightest sky direction within 15 degrees of -`SUN_DIR`).
- **How windows see it**: glass stays as in phase 1 (alpha-blended, casts no shadow). A Cycles portal sits 30 mm
  inside every `ctx.exterior_openings()` opening and under every roof window. Interiors receive sun + sky through the
  holes in the mass and the matching holes in the skin; what is seen through a window is the real site, envelope and
  neighbours.
- `lighting.fill(ctx, room)` only for kind `room` / `stairwell` without fittings; never outdoors. Its height is `zc =
  floor_z(room) + min(ceil_z(room) - floor_z(room), ceilingDefault)`, lowered at each rectangle centre to
  `ceil_z(room, x, y)`; lamps hang 0.35 below that. (Today `min(ceil_z, ceilingDefault)` puts every upper-floor fill
  at Z 2.6, inside the ground floor.) `lighting.downlight`'s default z = `ceil_z(room, x, y) - 0.015`.
- Lights-off set: unchanged rules (sun + sky + `AMBIENT_OFF`).
- **Viewer sky**: export renders the world alone (every object hidden) through the scene's view transform (AgX, look,
  exposure, the 3000 K balance) with a 2048 x 1024 equirect camera, centre +X like the probes, and saves the
  **displayed 8-bit image** `docs/assets/sky.jpg`. `manifest.sky = {image, color, sunDir}` (`color` = mean displayed
  colour as hex), no intensity. The viewer sets it as `scene.background` unchanged (`colorSpace` sRGB, equirect
  mapping, the probes' orientation): three.js does not tone-map an sRGB background, which is why phase 1 shipped the
  sky as a display colour. The dollhouse keeps its neutral background.

## 10. Export (agent e: `export.py`, `export_bake.py`, `export_check.py`)

```
blender -b build/home.blend --python blender/export.py -- --out docs/assets [--levels G,1] [--rooms a,b]
    [--bake-res 4096] [--samples 1024] [--density 160] [--skip-bake] [--skip-off] [--renders] [--house <path>]
```
- **GLB per level**: `glb/<level>.glb` for B, G, 1, 2, X = the objects with that `obj['level']`, same pipeline as
  today (flatten, `resize` / `webp` / `meshopt` only, `check_glb` per file). `home.glb` is deleted. `ix` passes
  through untouched.
- **Atlases**: key = `obj['room']` (a room that is neither a house room nor a pseudo-room -> `neighbours`, with a
  `WARNING` line: the phase-1 fixture has `shell`). Size = `atlas_size(m2, fill, density, cap)` as today (lightmapped
  surface at a fixed texel density, which yields 4096 / 2048 / 1024 by room size) with `density` 160 px/m for house
  rooms, 80 for exterior rooms (`ctx.is_exterior`), except 40 for `facade`, `roof`, `neighbours`; `cap` =
  `min(--bake-res, 4096 for house rooms | 2048 for exterior rooms, ATLAS_CAP.get(room))`. **`--bake-res` defaults to
  4096** (today 2048) and is only an upper bound. `ATLAS_CAP` is an empty dict in `export.py`: the one knob for
  trimming a room when a budget fails. Files `lightmaps/<room>.jpg`.
- **Lights-off set**: `lightmaps_off/<room>.jpg` (half size) for **every atlas except `facade`, `roof` and
  `neighbours`**, and `probesOff` for every probe. Switches name rooms that hold no lamp (`rooms=['hallway',
  'stairs']`; the landing lights also light `landing1_ql` and the `stairs2` well), and the viewer's fallback for a
  missing off atlas is 12 % of the on atlas, far darker than the real lights-off bake. export asserts that no `ix`
  `light` / `lamp` `rooms` list names `facade`, `roof` or `neighbours`.
- **Probes**: one per kind `room` / `exterior` / `stairwell` room and per `front`, `side_passage`, `garden`, `shed`
  (polygon = the largest walkable zone / the workshop), at floor + 1.5.
- **White balance**: the one matrix, as today, for every atlas and probe.
- **[integration] Encoding**: `intensity` = the 99.5th percentile of the lit texels, capped at 6 x the median of the
  texels brighter than 2 % of that percentile (faintly lit cabinet backs must not drag the median down: the kitchen
  atlas clipped to white at intensity 0.10 before); exterior atlases (sun and shade 10x apart) are capped by the
  percentile only.
- `--levels` / `--rooms` re-bake a subset; untouched entries are kept from the previous manifest.
- **Asserted budgets** (exit 1): every file < 50 MB; every GLB <= 40 MB; **`glb/G.glb` <= 21.5 MB**; first view =
  `glb/G.glb` + lightmaps and probes of the level-G rooms + manifest, house, plan and footprints json < 35 MB (the
  lights-off set loads lazily and does not count); `docs/` < 300 MB; triangles per level and total as section 5.
  **The first-view estimate is printed and asserted right after the GLBs are written, before any bake** (and in
  `--skip-bake` runs): GLB bytes + per atlas the existing file's size, or 2.7 MB x (size / 4096)^2 when there is
  none, + 0.1 MB per probe. Measured today: `home.glb` 20.2 MB at 742 k triangles, ground-floor atlases 10.8 MB,
  probes 0.7 MB = 31.7 MB, which is why level G is held to 0.85 M triangles.
- `export_check.py` takes `--level` and re-lights `build/export/<level>_raw.glb`.

**manifest.json, schema 2** (existing keys keep their meaning; new: `schema`, `levels`, `loadOrder`, `level` / `bytes`
on entries, `rooms[].level/kind`, `sky` object, `firstView`):
```json
{"schema": 2,
 "levels": [{"id": "G", "name": "Ground floor", "datumZ": 0.0, "cutZ": 2.33, "glb": "glb/G.glb", "bytes": 21100000,
             "triangles": 815000, "rooms": ["vestibule","hallway","stairs","living","kitchen","wc","utility","dining"]},
            {"id": "X", "name": "Outside", "datumZ": -0.3, "cutZ": null, "glb": "glb/X.glb", "bytes": 14100000,
             "triangles": 610000, "rooms": ["front","side_passage","garden","shed","facade","roof","neighbours"]}],
 "loadOrder": ["G", "X", "1", "2", "B"],
 "rooms": [{"id": "living", "level": "G", "kind": "room", "name": "Living room", "polygon": [[0.8,0.99]], "floorZ": 0, "ceilZ": 2.95},
           {"id": "balcony", "level": "1", "kind": "exterior", "name": "Balcony", "polygon": [[0.0,17.36]], "floorZ": 3.0, "ceilZ": null},
           {"id": "garden", "level": "X", "kind": "site", "name": "Garden", "polygon": [[-0.75,17.36]], "floorZ": -0.05, "ceilZ": null}],
 "lightmaps": [{"room": "living", "level": "G", "image": "lightmaps/living.jpg", "size": 4096, "pxPerM": 181,
                "intensity": 1.93, "bytes": 2310000, "objects": ["living.walls", "living.floor"]}],
 "lightmapsOff": [{"room": "living", "level": "G", "image": "lightmaps_off/living.jpg", "size": 2048, "intensity": 0.61, "bytes": 420000, "objects": ["living.walls"]}],
 "probes": [{"room": "living", "level": "G", "image": "probes/living.jpg", "pos": [2.6, 2.8, 1.5], "intensity": 2.4, "bytes": 90000}],
 "probesOff": [{"room": "living", "level": "G", "image": "probes_off/living.jpg", "pos": [2.6, 2.8, 1.5], "intensity": 0.5, "bytes": 30000}],
 "viewpoints": {"living": {"pos": [1.05, 4.3], "look": [3.6, 1.6]}}, "spawn": {"pos": [0.0, 3.0], "yaw": 0, "level": "G"},
 "toneMapping": "agx", "exposure": 0.6598, "whiteBalance": [[1,0,0],[0,1,0],[0,0,1]],
 "sky": {"image": "sky.jpg", "color": "#8fb4d9", "sunDir": [0.429, -0.807, 0.407]},
 "firstView": {"bytes": 33100000, "files": ["glb/G.glb", "lightmaps/living.jpg"]}, "encoding": "as schema 1"}
```
- **`rooms[]`** = every house room, plus `front`, `side_passage`, `garden` and `shed` with `polygon` = their largest
  walkable zone (shed: the workshop), `floorZ` = its z, `ceilZ` null, `kind` `"site"`. `facade`, `roof` and
  `neighbours` appear **only** in `levels[X].rooms` (they have no polygon; the viewer takes the centroid of every
  `rooms[]` polygon).
- `cutZ` = lowest `ceilingZ` of the level's kind-`room` rooms minus 0.07 (B -0.38, G 2.33, 1 5.28, 2 8.42); `X`: null.
  `levels[]` lists every level; `glb` is null where nothing is built and `loadOrder` holds only levels with a GLB.
  `datumZ` of `X` = the lowest floor of its `rooms[]` entries (-0.32, the shed workshop).
  `sunDir` is the unit vector **to** the sun in the house frame.

**footprints.json** (array; `level` = the level of `room`, so balcony furniture is `1` and a car is `X`):
```json
[{"name": "green_bedroom.bed", "room": "green_bedroom", "level": "1", "plan_sym": "bed",
  "obb": [[1.2,2.1],[3.0,2.1],[3.0,4.2],[1.2,4.2]], "zmin": 3.42, "zmax": 4.55, "height": 1.13},
 {"name": "front.car_grey", "room": "front", "level": "X", "plan_sym": "car",
  "obb": [[-0.2,-5.0],[1.5,-5.1],[1.7,-1.2],[0.0,-1.1]], "zmin": -0.06, "zmax": 1.45, "height": 1.51}]
```
Readers (plan, viewer) accept records without `level` (today's file has none): the level is that of `room` in
house.json; pseudo-rooms and building rooms -> `X`; an unknown room -> `G`.

**Plan symbols** (`plan_sym`), old list plus: `bed bedside wardrobe chest bureau desk office_chair bath shower vanity
sauna boiler cylinder rack cabinet workbench bench car planter fire_pit trellis flagpole condenser`. Viewer classes:
non-blocking `rug mirror tv wall_unit airer shelf towel_rail radiator stair trellis flagpole condenser`; soft (walk
through, slowed, when under 1.3 m) `chair armchair stool bin plant office_chair bedside`; everything else blocks.

## 11. Plan (agent f: `tools/plan/`) and viewer (agent g: `docs/`)

### 11.1 Plan sheets

- Sheets `B`, `G`, `1`, `2` at 1:50 on A3 and the site plan, **sheet id `X`**, title `SITE PLAN`, at 1:100 on A3, all
  in **world coordinates** (no per-sheet offset), so one (x, y) means the same place on every sheet. Level `1`
  includes the balcony: to keep 1:50 the vertical margins shrink to 48 mm (18.53 m x 20 + 48 = 419 mm).
- **Site sheet window** = the plot polygon's bounding box + 0.3 m: x -1.18..5.73, y -5.5..29.2 (69 x 347 mm at 1:100;
  `siteBounds` would need 430 mm of height and drop the sheet to 1:125). Everything (zones, footway, road,
  neighbours, boundaries, cars) is clipped to it. The scale is fixed at 1:100 and asserted, never picked.
- Poche of level L = envelope polygons of L minus every room of L (all kinds) minus `floor_void` polygons of L, plus
  inner walls and solid features, cut at the openings of L. Chamfers are drawn true, both kinds (the bay splays from
  `bay.chamfers`, computed as in section 3; the cut plane lies inside their `z`). Cut plane 1.2 m above each room's
  own floor.
- Stairs: a flight is drawn on the sheet of its lower end up to a break line with "UP", and on the sheet of its upper
  end beyond the break with "DN", risers from `walk.risers`; `steps` as riser lines with "UP 2R"; every split floor
  gets an FFL mark (`FFL +3.420`). Room tags carry FFL. Sloped ceilings: dashed 1.5 m headroom line; roof windows
  dashed.
- Site sheet: plot (dashed), zones with surface name and level (both ends of a `fall`), steps, boundaries, gate swing
  (50 degrees), shed with poche, house as outline + roof lines, cars and garden items from footprints (fallback
  `exterior.features`). New layers `L-SITE` (ACI 3), `L-SITE-BNDY` (ACI 1, dashed), `A-ROOF` (ACI 8).
- Footprints are filtered by `level` (fallback of section 10); new symbols of section 10 get drawn forms (bed with
  pillows, bath, shower tray with diagonal, sauna, car outline with wheels, etc.) on `A-FURN` / `A-FLOR-FIXT`.
- Outputs: `docs/assets/plan.json`, `house-plans.dxf`, `house-plans.pdf` (one A3 page per sheet in the order B, G, 1,
  2, site). The `ground-floor-plan.*` files are removed. `check.py` audits all sheets, rasterises each to
  `build/plan/<sheet>_*.png` and keeps the privacy scan.
- **DXF**: one model space, units mm, sheets side by side: sheet i is translated by its `dxfOffset`, given **in DXF
  millimetres**. `$LTSCALE` 1; the entities of the 1:100 sheet are written with linetype scale 2.0 (group 48) and
  DIMSTYLE `PLAN100` (text and ticks x 2), the others with `PLAN50`.

**plan.json, schema 2**. `units`, `layers`, `textNote` and `footprintSource` are shared at the top. `linestyles`,
`hatch` and `dimstyle` are model metres derived from the sheet scale, so they live **in each sheet**, with
`bounds` / `houseBounds` / `sheetBounds` / `entities` / `rooms` (what was at the top in schema 1):
```json
{"schema": 2, "units": "m", "layers": [], "textNote": "", "footprintSource": "footprints.json (312 items)",
 "sheets": [{"id": "1", "level": "1", "title": "FIRST FLOOR PLAN", "scale": "1:50", "paper": "A3", "orientation": "portrait",
             "bounds": {"minX": -1.3, "minY": -0.6, "maxX": 4.95, "maxY": 18.9}, "houseBounds": {}, "sheetBounds": {},
             "linestyles": {"dashed": [0.12, 0.06]}, "hatch": {"spacing": 0.09}, "dimstyle": {"h": 0.174, "tick": 0.065, "extGap": 0.06, "extBeyond": 0.08},
             "dxfOffset": [40000, 0], "entities": [{"layer": "A-WALL", "type": "polyline", "pts": [[0,0]], "closed": true}],
             "rooms": [{"id": "blue_bedroom", "name": "BLUE BEDROOM", "polygon": [[-0.65,12.52]], "floorZ": 3.04, "area": 15.1}]},
            {"id": "X", "level": "X", "title": "SITE PLAN", "scale": "1:100", "paper": "A3", "orientation": "portrait",
             "bounds": {"minX": -1.18, "minY": -5.5, "maxX": 5.73, "maxY": 29.2}, "houseBounds": {}, "sheetBounds": {},
             "linestyles": {"dashed": [0.24, 0.12]}, "hatch": {"spacing": 0.18}, "dimstyle": {"h": 0.347, "tick": 0.13, "extGap": 0.12, "extBeyond": 0.16},
             "dxfOffset": [160000, 0], "entities": [], "rooms": []}]}
```

### 11.2 Walk layers (viewer, `docs/js/geom.js`, built from `assets/house.json` + footprints)

Collision stays 2D. A **layer** is a set of cells that never overlap in plan; the visitor is on exactly one layer.
Layers: `B`, `G`, `1`, `2` and one per `kind: flight` stair (`stair_basement`, `stair_main`, `stair_second`). There is
no outdoor layer: ground-floor rooms and exterior zones never overlap in plan, so **the outside is part of layer `G`**
and a door to the garden is an ordinary door. The balcony is on layer `1`.

**Cells**
1. Level layers: every room of that level with kind `room` or `exterior`: polygon, `z = floorZ`, `treads` (from
   `steps` stairs whose `toRoom` it is: strip between `riserLines[k]` and `[k+1]`, `z = fromZ +- (k+1) * rise`),
   `planes` (from `ceiling.planes`, for headroom). Free = inside the polygon and >= `radius` from every edge (every
   edge is solid unless a portal of this layer bridges it, so balustrades and well edges block with no extra data).
2. Layer `G` also holds the **ground cell**: all zones with `walk != false`, their `z` or `fall` and `room`, and
   `steps[].treads`; lookup = first containing tread, else first containing zone, both sorted by area ascending
   (containment with 1 mm tolerance: zones share edges). Free = inside some zone and >= `radius + halfThickness` from
   every **blocker**: edges of the envelope polygons of level G, boundary lines (walls, fences, neighbour walls; a
   gate only while its portal is shut), pier polygons, shed wall rectangles, neighbour polygons. Walkable building
   rooms (`walk: true`) are ordinary cells of `G` carrying `room` = the building's room (`shed`), so the room label
   and the probe resolve.
3. Flight layers: one cell = `stairs[i].walk.polygon`. Floor Z is a ramp over the riser lines: with k = number of
   consecutive risers passed (point on the left of a->b) and d = distances to riser k and k+1, `z = fromZ + (toZ -
   fromZ) * (k - 1 + d_k / (d_k + d_k1)) / (n - 1)`, `fromZ` before the first riser, `toZ` after the last.

**Feature blockers**: projections are in `features`, not in the room polygons. `buildWalk` adds to the room's layer,
as blocking polygons like furniture, every feature of type `pier`, `pilaster`, `chimney_breast` or `boxing` with
`z[0] <= floorZ + 0.1` and `z[1] >= floorZ + 1.0` (the basement breast base, the landing pier, the WC duct; hearths,
soffits and overhead boxings are excluded).

**Portals** (rectangle: along = width / 2 - radius, at least 0.04; across = wall thickness / 2 + radius + 0.05,
exactly as `portalFor` today; flat list `walk.portals` with `id` and `open`, which is all `interact.js` uses):
- every opening of type door, double_door, french_door, arch, opening (never hatch) whose two `connects` ends resolve
  to cells: a walkable room -> its cell; `outside` -> the ground cell; a stairwell room -> the flight whose
  `walk.ends` names this opening. `open = openAngle !== 0`, switched by `ix` tags with `blocks`. Building openings
  likewise.
- every segment of `riserLines[0]` of a `steps` stair (thickness 0), joining `fromRoom` and `toRoom`; a line with one
  segment gets the id `<steps id>`, with several `<steps id>.<k>` (`steps_ql_rear.0`, `steps_ql_rear.1`).
- the side gate: portal on its line inside the ground cell, shut until its `ix` group opens.

Every portal carries `layers: [a, b]` and `cells: [idA, idB]`. **A portal exists only on its own layers**:
`isFree(walk, L, x, y)` is true inside an open portal only when L is in `portal.layers`; `nearestFree`, `route` and
`zAt` use the same filter. (Today's `isFree` accepts any open portal; ported unchanged, the open `d_basement` portal
would be a free island on layer `1`.)

**Moving**: a sub-step target that is free on the current layer is taken. Otherwise, if the visitor stands inside an
open portal that joins the current layer to another one and the target is free on that other layer, the layer switches
and the step is taken; otherwise slide as today. Nothing else ever changes the layer.

**Floor height** `zAt(layer, x, y)`: the cell of that layer containing the point (no inset) gives its Z (tread, zone
with `fall`, or ramp). A point **in a portal but in no cell** (inside a wall thickness) takes the Z of the nearest
walkable piece (room polygon, tread, zone polygon or flight ramp, by polygon distance) among the portal's cells on
that layer: `d_street` -> forecourt -0.06, `d_back` -> `kitchen_steps` tread -0.02, `d_french` -> deck -0.05,
`shed_d1` -> shed_veranda -0.42. `zAt` is therefore finite wherever `isFree` is true. Single risers, the two steps and
the 0.27 m loft step are instantaneous; the camera eases to the target height at rate 10 per second (`z += (target -
z) * min(1, 10 dt)`). Under `planes` the eye is the lower of 1.6 m and headroom minus 0.12 m; a point with headroom <
1.25 m is not free (loft knee walls).

**Level shown** `levelAt`: a room cell -> its level; the ground cell and building rooms -> `X`; a flight -> the level
of its lower end below mid-height, of its upper end above. The room label, the plan sheet and the dollhouse level
follow it.

**Routing** (double-click, plan click, room jump): A* nodes are (layer, i, j); neighbours as today inside a layer,
plus a zero-cost link to the same (i, j) on the other layer of any open cross-layer portal containing the node.
String-pulling only inside runs of one layer. A double-click target takes the layer whose `zAt` is nearest the hit
point's height (floor hits within 0.3 m, wall hits within floor..floor + 2.6). A plan click targets the layer of the
sheet (`X` -> `G`). Room jumps to another layer cut with a 150 ms fade instead of flying through floors.

**Narrow passages** (radius 0.15): basement door 0.61 -> 0.31 m lane; basement shaft 0.665 -> 0.365; loft door 0.61 ->
0.31; stair foot 0.50 -> 0.20; quarter landing 0.60 deep -> 0.30. Section 16 traces them. Walls inside one room (arch
walls) are not obstacles: jambs intrude <= 0.10 m.

**The structure `buildWalk(house, {obstacles, soft})` returns:**
```json
{"radius": 0.15, "layers": ["B","G","1","2","stair_basement","stair_main","stair_second"],
 "cells": [{"id": "landing1_front", "layer": "1", "level": "1", "kind": "room", "room": "landing1_front", "polygon": [[-0.65,4.95]], "z": 3.42,
            "treads": [{"polygon": [[-0.65,8.13],[0.15,8.13],[0.15,7.88],[-0.65,7.88]], "z": 3.23}]},
           {"id": "shed_workshop", "layer": "G", "level": "X", "kind": "room", "room": "shed", "polygon": [[-0.6,25.28]], "z": -0.32},
           {"id": "ground", "layer": "G", "level": "X", "kind": "ground",
            "zones": [{"id": "deck_step_e", "room": "garden", "polygon": [[3.4,17.75]], "z": -0.25},
                      {"id": "deck", "room": "garden", "polygon": [[-0.75,17.36]], "z": -0.05},
                      {"id": "forecourt", "room": "front", "polygon": [[-0.72,-5.2]], "z": -0.06,
                       "fall": {"from": [1.9,-0.12], "to": [1.9,-5.2], "z": [-0.06,-0.14]}}],
            "treads": [{"polygon": [[3.4,9.03],[4.35,9.03],[4.35,9.33],[3.4,9.33]], "z": -0.02}],
            "blockers": [{"a": [-0.88,-0.12], "b": [4.15,-0.12], "half": 0}, {"a": [4.5,9.03], "b": [4.9,9.88], "half": 0.03, "portal": "side_gate"}]},
           {"id": "stair_main", "layer": "stair_main", "level": ["G","1"], "kind": "flight", "polygon": [[0.15,5.05]],
            "fromZ": 0, "toZ": 2.85, "risers": [[[0.2,5.33],[0.65,5.05]]]}],
 "portals": [{"id": "d_basement", "layers": ["G","stair_basement"], "cells": ["hallway","stair_basement"], "open": false,
              "center": [0.57,7.63], "normal": [0,1], "depth": 0.05, "width": 0.61, "poly": [[0.415,7.38],[0.725,7.38],[0.725,7.88],[0.415,7.88]]},
             {"id": "steps_ql_rear.0", "layers": ["1","1"], "cells": ["landing1_ql","landing1_rear"], "open": true, "poly": []}],
 "obstacles": {"G": [], "1": []}, "soft": {"G": []}}
```
`obstacles[layer]` holds the furniture footprints and the feature blockers of that layer.
`geom.js` exports: `buildWalk`, `isFree(walk, layer, x, y)`, `isSoft(walk, layer, x, y)`, `move(walk, pos, x1, y1) ->
{x, y, layer}`, `zAt(walk, layer, x, y)`, `headroomAt`, `cellAt`, `levelAt`, `nearestFree(walk, layer, x, y, maxR)`,
`route(walk, a, b) -> [{x, y, layer}] | null`, `viewpoints(walk, spawn)`, `obstaclesFrom(fp, soft, house) -> {layer:
[poly]}` (level fallback of section 10; level `X` -> layer `G`), plus the unchanged frame helpers.

### 11.3 Viewer behaviour (`main.js`, `plan2d.js`, `interact.js`, `index.html`, `style.css`, tests)

- **Loading**: manifest, house, plan, footprints; build the walk; load `levels[].glb` in `loadOrder`, adding every
  level scene under **one root Group** and applying lightmaps and probes of a level as it arrives; the loading screen
  goes when level G is lit, the rest streams in behind a small progress chip. A level without a GLB is still walkable
  (tests). Lights-off images load on the first switch use. On coarse-pointer devices atlases larger than 2048 are
  downscaled on load. Schema-1 assets (no `levels`) keep working: one level `G`, `home.glb`.
- **Interactions**: `initInteract` walks one model once: it builds the groups, re-parents pivots, clones materials
  and registers lamp emissives only for meshes present at that moment, and it cannot run twice over the same nodes.
  Switches control rooms on other levels (`landing1.md` 8.2: the ground-floor hall plate switches the level-1 landing
  downlights, a level-1 plate the level-2 landing lights). **[integration, question 17.2 decided]** Interactions are
  incremental: `initInteract({...})` returns an engine and `main.js` calls `engine.add(levelScene)` once per level as
  its GLB arrives; each node is processed once, switch rooms are registered as they appear and lamps of rooms that
  arrive later are attached then. The export fails if one `ix` group has members in two level GLBs. `interact.js`
  belongs to the viewer owner. `initInteract` also takes `feetY: () => number` (the walker's floor height in three.js Y) and `reachTo` clamps
  the body column to `[feetY() + 0.2, pos.y]` instead of the absolute `[0.2, pos.y]`, which collapses in the basement
  and reaches down through the floors upstairs.
- **Walk mode**: every loaded level is drawn (upper floors are seen through the stair wells, the site through the
  windows). State gains `layer` and `z`; camera Y = z + eye.
- **Dollhouse**: level buttons B G 1 2 and "All"; one clipping plane at `levels[].cutZ` removes everything above the
  selected level (floors above, roof, upper skin); "All" clips nothing. **`B` also hides the `X` GLB** (visibility,
  not clipping: the lawn and shed feet would float beside the basement). The orbit target sits on the level's
  `datumZ`. Section caps as today. **[phase 2]** Visibility (`dollVis`, set on `visible`, never on an `ix`-tagged
  object, whose visibility belongs to `interact.js`): the pseudo-room `neighbours` is hidden in every dollhouse view;
  on a level cut also every mesh wholly above `cutZ`, every `roof` mesh rising more than 1.2 m above the level's
  `datumZ` (the loft slopes sit below the level-2 cut; the porch lean-to and the rear flat roof stay beside level 1)
  and every `<room>.ceiling` of a room of that level. "All" shows house, roof, garden, shed and forecourt. When
  `levelAt` is `X` (and on a click on the SITE sheet) the dollhouse level is **"All"**, no extra button. **Framing**
  (`frameBox`, on entering the dollhouse and on a level button; plan clicks and room jumps only move the target): the
  box is the level's room polygons from `datumZ` to `cutZ` ("All": `exterior.plot.polygon`, `X.datumZ` to the highest
  `cutZ` + 1). Of eight compass directions 57 deg up (66 deg on a portrait screen) the one that shows the box largest
  wins (side-on on a wide screen; ties go to the side the camera was on), at the distance that puts every corner of
  the box inside 85 % of the part of the view the open plan panel leaves free (its left on a wide screen, its top on a
  phone). A camera view offset (`applyViewShift`: `setViewOffset` with a 70 deg view kept in the free part) centres
  the target in that part, so the target - plan marker, orbit pivot, the spot "Walk" returns to - stays on the house;
  it follows the panel (collapse, maximise, resize) and is cleared in walk mode. `orbit.maxDistance` = max(60, 1.6 x
  the fit distance).
- **Room bar** **[phase 2]**: one group per level (B, G, 1F, 2F, OUT) with a floor chip; only the open group lists its
  room buttons (short names: `/`, `(`, ` and ` cut, "room", "First-floor" / "Second-floor" dropped; the full name is
  the tooltip). The open group is the visitor's level, re-opened whenever the level changes; a chip click or PageUp /
  PageDown opens another until then. Digits 1-9 jump within the open group. The current room's button is scrolled
  into view on every room change; a vertical mouse wheel scrolls the strip sideways (it has no scrollbar).
- **Textures** **[phase 2, E-TEXMEM]**: the export writes an image into every level GLB that uses it. `prepare`
  keeps one `THREE.Texture` per image `name` + size + sampling (colour space, wrap, channel, flipY, offset, repeat,
  rotation) for all level scenes; unnamed images are never merged. Phones (coarse pointer, or a screen under 600 px
  on its short side) draw GLB colour maps (`map`, `emissiveMap`) over 512 px down to 512 before upload; lightmaps
  over 2048 as before. Measured on `build/export_int` with every level loaded (decoded RGBA + mips of every texture
  source the scene draws; `viewer.texStats()` uploads what is not on the GPU yet and returns `{gpuTextures, sources,
  MB}`): GLB textures 177 sources / 539 MB before, 149 / 471 MB shared (desktop), 170 MB on a phone; with lightmaps
  and probes 705 -> 637 MB (desktop), 336 MB (phone); `renderer.info.memory.textures` 277 -> 249. The rest of the
  desktop figure is unique images: 67 colour maps over 512 px remain at full size there.
- **Effects** **[phase 2]**: `fx water` sizes its streaks from the mesh as modelled (no tag key): girth g = surface
  area / height (a curved stream or a splash ring at its foot hardly changes it; the bounding box does). Every water
  object gets its own clone of the streak texture repeated round(g / 0.04) (>= 1) times round the girth and
  round(h / 0.12) (>= 2) down the length, double-sided; g > 0.2 m is a spray (a shower cone): jets with clear gaps
  between them and opacity x 0.7. A tap stream keeps one repeat round. `fx flame` takes the hue of the object's emissive when it
  is not black (blue gas hob, orange fire pit), else gas blue.
- **Sky**: `manifest.sky.image` as equirect `scene.background`, unchanged (section 9); fallback `sky.color`; a
  schema-1 `sky` is a hex string. Emissive colours keep the white-balance matrix.
- **Probes**: a mesh uses the probe of its `room`; without one, the nearest probe **of the same exterior-ness**:
  meshes of level `X` or of a kind-`exterior` room (facade, roof, neighbours, gutters) choose among the `front`,
  `side_passage`, `garden`, `shed` and `balcony` probes, all others among the interior probes.
- **Plan panel**: tabs B G 1 2 SITE (sheet ids B G 1 2 X); the sheet follows `levelAt` whenever the visitor's level
  changes, a tab click overrides until the next change. Marker and view cone are drawn on the sheet of the visitor's
  level and always on SITE (hollow when indoors). Click = walk / teleport on that sheet's layer.
  `PlanView.setSheet(id)` re-reads the sheet's `linestyles`, `hatch`, `dimstyle` and bounds; room highlight from the
  sheet's rooms. Downloads point to `house-plans.dxf` / `.pdf`. Room buttons are grouped by level (see Room bar).
- **Lights off** **[phase 2]**: a switch loads the lights-off lightmap and probe of exactly the rooms in its `rooms`
  list, on its first use (`ensureOff`; the fade waits for them), whatever level they are on; until then a room's
  materials sample its lights-on atlas in the off slot (no extra texture). Rooms of a level that arrives after the
  switch was used pick up the current state (shared `lmOn` uniform, emissives registered at `engine.add`).
- **Light uniforms of a lightmapped material** (`specOnly` in `main.js`): `lmOn` (the room's light state, 1 = lights
  on), `lightMapOff` / `lightMapOffIntensity` (the room's lights-off atlas), `lmMix` (1 = bake; `interact.js` fades a
  baked door leaf or front toward 0 as it leaves its modelled pose, because the bake only fits that pose) and
  **`lmProbe`**: the probe light that replaces the bake as `lmMix` falls, `iblIrradiance += (1 - lmMix) * lmProbe *
  getIBLIrradiance(n)`. `lmProbe` = the light the bake gave the face that looks the way the leaf swings (its
  surroundings once open: the deck for a French door, the vestibule for the street door), area-weighted from a 512 px
  copy of the atlas, over the probe's irradiance (`lmProbeScale`, clamped 0.05..1.5; one value per leaf), so an
  exterior leaf does not jump to its room's brighter probe.

**Door leaves are moving walk obstacles** (`geom.js`, driven by `interact.js`). `walk.dynamic` = `[{id, layers, poly,
bb}]`; `setObstacle(walk, id, layers, poly)` replaces (or with `poly` null removes) one; `dynDist(walk, L, x, y)` is
the distance to the nearest moving obstacle of layer L (0 inside). `isFree` rejects points within the body radius of
one, like a fixed obstacle. `interact.js` (`syncPortals`, on every add and toggle) gives each hinge group with a
vertical axis and `blocks`, and each slide group with `blocks`, the convex hull of its meshes in plan at the pose it is
heading for (set at once, not per frame), on the layers of its doorway's portal (else the layer of its level). A
portal is open while any leaf that blocks it is open, so a double door with one leaf open keeps its shut leaf's half
solid and the route goes round it. A walker left inside a doorway that shuts is moved to the nearest free spot
(`onPortals`). Tests open a doorway through its leaf (`ix.toggle` of the group whose `blocks` names it); only the
fixture, whose GLB has no leaves for the new doorways, sets `portal.open` directly.

**Viewpoint fields**: `viewpoints(walk, spawn)` -> `{room: {pos, yaw, layer, pitch?, into?}}`. `pitch` (radians, < 0
looks down) is set where the view would face a wall close by with nothing deeper: the quarter landing looks back
down the main flight at -0.35. `into` is the unit plan vector from the viewpoint's doorway into the room; a room jump
steps on along it (up to 1.2 m, 0.15 m at a time, while free) until no open leaf is within 0.6 m (`dynDist`), so a
leaf standing open beside the doorway does not fill the view. Hand-framed `manifest.viewpoints` replace `pos` / `yaw`
when they snap (`nearestFree` within 0.6 m) into their own room; the room holding the spawn keeps the spawn view.

## 12. Agents

Common to all: test against `build/fixtures/house2.json`; README text goes into the agent's **own** file
`blender/lib/README.<module>.md` (never into `blender/lib/README.md`, which the orchestrator merges at integration).
Generated files under `docs/assets` belong to the tool that writes them (export, plan).

### a. core
- **Owns**: step 0 (`spec/adopt_house2.py`, `spec/validate_house2.py`, `build/fixtures/house2.json`, `lib/ctx.py`),
  then `lib/shell.py`, `lib/stairs.py` (new), `lib/lighting.py`, `lib/preview.py`, `build.py`, `blender/test_ctx.py`
  (new), `README.ctx.md`, `README.shell.md`, `README.lighting.md`, `README.build.md`.
- **Provides**: sections 2-5 and 9; every ctx name of section 3; `shell.build(ctx, levels=None)`,
  `shell.wall_runs(ctx, room, z=0.05)`, `shell.remove(room, part)`, `shell.surface`, `shell.repaint`, `shell.box`
  (unchanged), `stairs.carcass(ctx, stair_id) -> Object`, `lighting.setup(ctx, samples, res)`, `lighting.fill(ctx,
  room)`, `lighting.downlight(...)` (signature unchanged), `FINISHES` for all rooms, build.py flags.
- **May assume**: joinery / trim / site / envelope may be missing (`--bare`, tolerant calls); material keys may be
  missing (grey fallback).
- **Tests alone**: `blender -b --python blender/test_ctx.py` (asserts on the fixture: 28 rooms, levels, chamfers p /
  q / c of both kinds, `ext_reveal` examples, `roof_slab_t`, `zone_z` at both ends of each fall, `d_balcony` outward);
  `build.py --house build/fixtures/house2.json --only shell --bare --preview
  plan:B,plan:G,plan:1,plan:2,section,level:1` at 540 px, and once with `--levels 1`.
- **Acceptance**: validator OK; `BUILD OK`; floor-area check passes for every non-stairwell room, also with
  `--levels 1`; no face outside the roof planes in `section`; chamfers (incl. the four bay splays with their stops),
  haunches, loft slopes, wells, risers visible and matching the validator previews; `o_basement_foot` head at -0.46;
  hearth and WC duct tops keep their finishes; upper-floor fills light the upper floors; kind-`shell` of house rooms
  <= 60 k triangles; a schema-1 `spec/house.json` still loads through the new ctx.

### b. site
- **Owns**: `lib/site.py`, `blender/test_site.py` (both new), `README.site.md`.
- **Provides**: `site.build(ctx)`, `site.surface(zone_id) -> Object`, `site.ZONE_MAT`.
- **May assume**: the step-0 ctx (`zone`, `zones_of`, `zone_z`, `opening_frame` for shed openings, `tag_room`);
  `M.mat` keys may be missing (its test patches a fallback); no shell, envelope or joinery.
- **Tests alone**: `test_site.py`: build site only, sun + sky stub, top view and four eye-level renders.
- **Acceptance**: every zone top within 1 mm of `ctx.zone_z` at its polygon vertices; zones gap-free and touching the
  envelope polygon; gate tagged, leaf bottom -0.14, state-1 pose (`IX.pose`) clear of both treads; shed objects
  tagged `shed`; previews match `spec/rooms/garden.md`, `front.md`, `shed.md` reference frames; <= 100 k triangles.

### c. envelope
- **Owns**: `lib/envelope.py`, `blender/test_envelope.py` (both new), `README.envelope.md`.
- **Provides**: `envelope.build(ctx)`, `envelope.roof_surface(x, y) -> z`.
- **May assume**: the step-0 ctx (`opening_frame` with `ext_reveal` / `face_out`, `roof_z`, `roof_slab_t`,
  `roof_under`, `zone_z`, `facade_of`, `exterior_openings`); material keys may be missing; no shell or site.
- **Tests alone**: `test_envelope.py`: skin + roof + balcony, orthographic front / rear / flank / roof-plan renders.
- **Acceptance**: holes line up with the opening list of each facade (assert on face bounds); roof watertight from
  above (ray grid hits roof, never a ceiling); **a horizontal ray grid from the four sides at Z 0..9.2 hits skin or
  roof, never nothing** (catches the roof-step faces and the base); slab undersides: pitched 0.30, flat 0.24; no skin
  above the roof surface; no envelope vertex inside a room polygon between its floor and ceiling; valleys correct;
  previews match `spec/phase2/*_elevation.md`; <= 150 k triangles.

### d. joinery / mouldings / materials
- **Owns**: `lib/joinery.py`, `lib/mouldings.py`, `lib/materials.py`, `blender/textures/**`,
  `blender/test_joinery.py` (new), `README.joinery.md`, `README.mouldings.md`, `README.materials.md`.
- **Provides**: `joinery.install_openings(ctx)`, `joinery.build_opening(ctx, oid)`, `joinery.validate(ctx) -> [str]`,
  `mouldings.room_loops(ctx, rooms, z, solids=())`, `mouldings.trim_runs(ctx, rooms, z, cfg=None)`,
  `mouldings.install_room_trim(ctx, room_id)`, `mouldings.TRIM`, `materials.mat(key)`, `materials.paint(hex)` — the
  phase-1 signatures, with `z` now world Z.
- **May assume**: the step-0 ctx (`opening_frame` z0 / `ext_reveal` / `outward`, `chamfers`, `FRAME_D`, `tag_room`);
  no multi-level shell yet.
- **Tests alone**: `test_joinery.py`: for each opening id a wall slab with the hole from `opening_frame`,
  `build_opening`, render both sides; `trim_runs` asserted on living (diagonal run and both bay splays in the
  skirting, square corners in the cornice), hallway at Z 0.05 (no cut from `w_green_rear`), stairs, landing1_rear
  (diagonal run), green_bedroom at Z 3.47 (door gaps present): closed loops, expected run counts.
- **Acceptance**: `joinery.validate` empty on the fixture; every material key of section 8 resolves; each new style /
  surround rendered and compared with its `spec/rooms/*.md` frames; `d_balcony` leaves open onto the balcony;
  state-1 poses collide with nothing.

### e. export
- **Owns**: `export.py`, `export_bake.py`, `export_check.py`, `blender/export_fixture.py` (new), `README.export.md`.
- **Provides**: section 10 (CLI, files, manifest schema 2, footprints with `level`, sky image, budgets).
- **May assume**: `obj['level']` and a tagged `obj['room']` on every object; house.json schema 2; the step-0 ctx.
- **Tests alone**: `export_fixture.py` opens the phase-1 `build/home.blend`, tags `level='G'`, copies kitchen + wc
  objects to +3.42 as `green_bathroom` (level 1), adds a ground quad `garden` (X), saves `build/fx_levels.blend`;
  export it to `build/export_fx` with `--house build/fixtures/house2.json --samples 64`.
- **Acceptance**: three GLBs; manifest schema 2 valid, `rooms[]` without `facade` / `roof` / `neighbours`; `check_glb`
  per level; first-view estimate printed before the bake and asserted; off atlas for `green_bathroom` and `garden`;
  `sky.jpg` is a displayed 8-bit image; `export_check.py --level 1` re-lit correctly.

### f. plan
- **Owns**: `tools/plan/**`.
- **Provides**: section 11.1: `draft.py [--house PATH] [--footprints FILE] [--out DIR]`, `check.py [--assets DIR]`,
  plan.json schema 2, `house-plans.dxf`, `house-plans.pdf`.
- **May assume**: footprints may lack `level` and whole rooms (level fallback, spec fallback, empty rooms allowed).
- **Tests alone**: `draft.py --house build/fixtures/house2.json --out build/plan_fx && check.py --assets
  build/plan_fx`.
- **Acceptance**: five sheets; site sheet at exactly 1:100 inside the stated window; per-sheet style tables; DXF
  audit clean with both dimstyles; PDF five A3 pages, vector; dims close on every sheet; bay splays and diagonal
  walls drawn true; rasters read and compared with `build/fixtures/plan_*.png`.

### g. viewer
- **Owns**: `docs/index.html`, `docs/style.css`, `docs/js/main.js`, `docs/js/geom.js`, `docs/js/plan2d.js`,
  `docs/test/**`, and in `docs/js/interact.js` only the `feetY` change of 11.3, made after the interaction workflow
  has landed.
- **Provides**: sections 11.2 and 11.3; the `geom.js` exports listed there; `PlanView.setSheet(id)`.
- **May assume**: assets may be schema 1 or 2; any level GLB may be missing; footprints may lack `level`.
- **Tests alone**: `HOUSE=build/fixtures/house2.json node docs/test/geom.test.mjs`; `docs/test/make_fixture.mjs`
  writes `build/e2e/assets2` (schema-2 manifest wrapping today's `home.glb` as level G, house.json = the fixture, no
  other GLBs); `e2e.mjs --assets build/e2e/assets2`.
- **Acceptance**:
  - geom: the routes of section 16 found by `route` with the Z sequences listed; shutting `d_basement` makes the
    basement unreachable; (0.57, 7.0) is free on three flight layers and not on `G`; with all doors open the
    `d_basement` portal centre is not free on layer `1`; `zAt` is finite at every 5 cm grid point of every open
    portal on both of its layers; the basement breast base blocks.
  - e2e, **two runs**: the phase-1 checks run on `docs/assets` as it stands (schema 1). On `build/e2e/assets2` only
    the schema-2 checks run (tabs, sheets, marker on every sheet, sheet follows the stairs, layers, routes, dollhouse
    cut per level, `initInteract` called once); the door, jamb and wall-hit checks are skipped there, because that
    fixture pairs the phase-1 GLB with the new geometry (`d_understairs` leaf, moved walls).

## 13. Full re-run and integration

```bash
B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
python spec/validate_house.py
"$B" -b --factory-startup --python blender/build.py -- --save build/home.blend              # BUILD OK
"$B" -b --factory-startup build/home.blend --python blender/export.py -- --out docs/assets --samples 1024 --renders   # EXPORT OK (--bake-res defaults to 4096)
python tools/plan/draft.py && python tools/plan/check.py                                     # PLAN OK / CHECK OK
node docs/test/geom.test.mjs && node docs/test/e2e.mjs
```
**[integration]** Before publishing, the whole chain runs against a scratch export: `export.py --out build/export_int
--tmp build/export_int_tmp --bake-res 1024 --samples 128`, `draft.py --footprints build/export_int/footprints.json
--out build/export_int`, `check.py --assets build/export_int`, `e2e.mjs --assets build/export_int`.
Spec or `blender/lib` changed -> everything. One room module -> build, `export --rooms <room>` (plus `--levels <its
level>` for the GLB), plan, tests. `tools/plan` -> plan, tests. `docs/js` -> tests.

Order of the foundation work: **step 0** (core alone) -> a to g in parallel on the fixture -> integration by the
orchestrator once the interaction workflow has finished: swap the spec files (section 2), merge the `README.*.md`
files, land core, then d, b, c (any order), then e, f, g against a real build. The foundation build is `--only
shell,site,envelope` until the room modules are re-fitted.

## 14. Deviations from the orchestrator decisions

1. **(1) Adoption timing**: `spec/house.json` is replaced at integration by the orchestrator, not by the foundation
   agents: `build.py` and `export.py` of the running interaction workflow read that file, and BRIEF forbids agents
   state-changing git commands. Until then everyone works on `build/fixtures/house2.json`.
2. **(3) Shell mechanism**: the grid starts from the solid envelope mass and carves rooms, instead of filling wall
   rectangles. Same result for axis-aligned walls, and it is the only way the floor zones, the poche behind the
   45-degree walls and the unseen zones come out solid without a list of special cases. Wall `height` no longer shapes
   anything except inner walls.
3. **(3) wall_runs / mouldings**: `mouldings` never used `shell.wall_runs`; it has its own `room_loops`. Both get
   Algorithm C; `wall_runs` returns diagonals for room agents.
4. **(2) Levels**: an object's level is its room's level, and house.next.json makes the balcony a level-1 room, so it
   is `1`, not `X`. Pseudo-rooms are `front side_passage garden shed facade roof neighbours`.
5. **(4) `lib/stairs.py`** is justified (three flights, soffits) and belongs to core; it builds flight carcasses only.
6. **(6) Atlas size** follows lightmapped surface at a fixed texel density (the existing `atlas_size`), which gives
   4096 / 2048 / 1024 by room size; a cap by floor area alone would drop the vestibule and the stairs from today's
   2048 to 1024.
7. **(6, 7) Progressive loading and interactions**: levels stream in, but things become operable only after the last
   GLB, because `initInteract` is one-shot and switches reach across levels (11.3).
8. **(7) Layers**: no outdoor layer and no layer change at exterior doors (section 11.2).
9. **(8) 1:50**: the level-1 sheet needs tighter margins because of the balcony; the site sheet shows the plot
   window, not the whole of `siteBounds`.

## 15. Assumptions and unverified numbers

- **Compass orientation is unknown**, so the sun azimuth is a look decision (kept from phase 1: from the front right).
  With the neighbours' massing the garden is mostly sky-lit at 24 degrees. One constant changes it.
- Blender 5.1 sky enum names and the values of `SKY_STRENGTH` / `SKY_TINT` were not run (no Blender allowed for this
  task): the contract fixes calibration targets instead of verified numbers.
- Winder riser lines of `stair_second`, the side alley (levels, the 0.12 drop at its street end) and the east
  elevation are assumptions in the spec; the roof plane polygons overlap and need the valley cut.
- The side gate's raised leaf and 50-degree stop follow from the spec's tread positions (+-0.04), not from footage:
  the gate is never operated on camera.
- The first-view budget rests on today's measured files; the re-fitted ground floor may bake larger atlases. The
  early estimate and `ATLAS_CAP` are the guard.
- Texture duplication across five GLBs and GPU memory for all atlases on phones are only known after the first full
  export; the fallback is the downscale rule in 11.3.
- The contract relies on these properties of the interaction engine as it stands now: `walk.portals[].id/open`, `ix`
  passing through the export untouched, and `initInteract`'s one-shot semantics (one model, one call, lamp emissives
  registered at that call).

## 16. Route traces

Simulated by the architect on the rules of 11.2 (A* on a 5 cm grid, radius 0.15) before this revision. The revision
changes `zAt` inside wall thicknesses (routes 4-6, where the earlier rule had no value), the portal layer filter, the
zone falls and the feature blockers; g's geom test re-proves every route. `[z]` = floor Z; doors named "open" are shut
in the model and opened first.

1. **Front door -> basement** (11.9 m): `G` vestibule [0] > d_inner > hallway [0], passage beside the stairs to the
   lobby > **d_basement** (open; portal x 0.415..0.725, y 7.38..7.88; switch `G` -> `stair_basement`) > ramp over 11
   risers [0 .. -2.31], shaft lane x 0.415..0.78, turning east at the winders > **o_basement_foot** (portal x
   0.73..1.45, y 5.34..5.85; switch -> `B`) > basement [-2.31].
2. **Front door -> blue bedroom balcony** (17.8 m): `G` vestibule > d_inner > hallway [0] > **o_stair_foot** (portal x
   0.30..0.50, y 4.85..5.25; switch -> `stair_main`) > ramp [0 .. 2.85] > **o_ql_main** (switch -> `1`) > landing1_ql
   [2.85] > steps_ql_rear.0 (portal on x 0.15) > landing1_rear [3.04] > a_landing1 > d_blue > blue_bedroom [3.04] >
   d_balcony (open) > balcony [3.00].
3. **Front door -> loft office** (18.8 m): as 2 to landing1_rear [3.04] > steps_rear_front (portal on y 8.13) >
   landing1_front tread [3.23] > landing1_front [3.42], south along the strip to the front landing >
   **o_stairs2_foot** (switch -> `stair_second`) > ramp [3.42 .. 6.02] over 10 straight risers and 3 winders turning
   west > **o_stairs2_head** (switch -> `2`) > landing2_head [6.02] > step_head_platform > landing2_platform [6.22] >
   d_loft (0.27 step) > loft_office [6.49]; eye lowers under the slopes, no entry where headroom < 1.25.
4. **Kitchen back door -> side passage -> garden -> shed** (19.4 m, all on `G`): kitchen [0] > d_back (open; in the
   outer half of the wall [-0.02]) > treads [-0.02, -0.16] > side_passage [-0.30] > passage step > garden_path [-0.45]
   (over deck_step_e [-0.25] when cutting the corner) > shed_veranda [-0.42] > shed_d1 (open) > shed_workshop [-0.32].
5. **Dining French doors -> deck** (2.2 m): dining [0] > d_french (open; outer half [-0.05]) > deck [-0.05].
6. **Street doors -> forecourt** (2.1 m): vestibule [0] > d_street (open; outer half [-0.06]) > forecourt [-0.06,
   falling to -0.14 at the footway].
7. Extra: side_passage > side gate (open) > side_alley [-0.30 rising to -0.20] > forecourt_alley_mouth [-0.08]; it
   only works with gap 4.

## 17. Open questions for the orchestrator (both decided at integration)

1. **One 3000 K balance outdoors.** The contract follows decision 5 and keeps the exterior from turning blue with a
   warm `SKY_TINT` on the physical sky, which makes the sky paler and warmer than a real late afternoon. If the first
   `elev:front` and garden previews are not acceptable, the only other route is a second, cooler balance for exterior
   rooms; that needs joinery to split the outer faces of every exterior frame, leaf and cill into `facade` objects.
   Decide after core's calibration previews.
   **Decided:** one balance stays. The calibrated lamp-coloured sky lights the scene at `SKY_STRENGTH` 0.6 and the
   camera sees a display sky (section 9). The sun position is unchanged; whether the garden should get direct sun
   is a look decision for the owner (`SUN_AZIMUTH`, `SUN_ELEVATION`).
2. **Interactions wait for the last level.** With one `initInteract` call, doors and switches do not respond until all
   five GLBs have arrived (first view < 35 MB, whole property possibly 100 MB+). Accept this, or commission an
   incremental `initInteract` (a larger change to a file the interaction workflow owns)?
   **Decided:** incremental (11.3).
