# shed - round-3 brief

Modules `blender/rooms/shed.py` (veranda, store and fittings; six literal coordinates) and `shed_workshop.py` (one); the
shed building (walls, roof, doors, windows) is built by the site stage and joinery. Decisions: `spec/RECONCILE3.md`
(garden-12..-18).

## (a) What moved

- **Building moved north and its front was resized.** Outline y 23.40..28.90 -> **25.02..30.75** (x -0.87..4.45 kept).
  Front wall `shed_w_front` y 25.14 -> **26.84** (outer face 26.70); rear wall `shed_w_rear` 28.76 -> **30.61**; side walls
  x -0.735 / 4.315 kept, now y 25.02..30.75 (south of 26.70 the east one is the veranda wing wall with the hook rail).
- **Veranda** `shed_veranda` x 0.06..4.22, y **25.02..26.70** (1.68 deep to the door threshold); new zone
  `shed_store_apron` x -0.35..0.06, y 25.35..26.70 (the paving running behind the front pier to the store doors; inferred,
  not seen).
- **French doors `shed_d1`**: centre (3.35, 25.14), 1.20 x 2.08 -> **(3.33, 26.84), 1.69 x 2.33** (frame x 2.485..4.175).
- **Window `shed_w1`**: (1.80, 25.14), 1.30 x 1.00, sill 1.05 -> **(1.00, 26.84), 2.00 x 1.22, sill 1.09** (frame x
  0.00..2.00, head level with the door head).
- **Store**: wall `shed_w_store` x -0.36 kept, y 23.75..24.98 -> **25.35..26.68**; doors centre (-0.36, 24.365) -> **(-0.36,
  26.02)**, width 1.23; store room x -0.77..-0.37, y **25.35..26.68**, ceiling 1.83 -> 2.02; front pier x -0.87..0.06, y
  25.02..25.35 (no spec field: build it in shed.py).
- **Workshop** room x -0.60..4.18, y 25.28..28.62 -> **26.98..30.47** (4.78 x 3.49); ceilingZ 1.98 -> **2.13** (2.45 above
  the floor -0.32, a guess); rear window `shed_w2` y 28.76 -> **30.61** (size unchanged). Keep the layout, stretch the
  clearances.
- **Roof** (new fields, not yet read by lib/site.py): `verandaSoffitZ` 1.83 -> **2.02**; `topZ` 2.25 -> **2.40** (felt 2.30
  at the front gutter rising to about 2.50: `felt`); pale concrete **coping on the west, rear and east** parapets 0.30
  wide, top Z **2.70** (`coping`; the side and rear walls are 3.12 high from -0.42); white fascia Z 1.98..2.20 (`fascia`)
  and white half-round gutter, rim 2.29 (`gutterRimZ`), along the whole front; white downpipe down the SW corner. The
  side copings end at the front as the pier caps (no separate taller piers).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `exterior.zones[shed_veranda].polygon`: [[-0.35, 23.4], [4.22, 23.4], [4.22, 25.0], [-0.35, 25.0]] -> [[0.06, 25.02], [4.22, 25.02], [4.22, 26.7], [0.06, 26.7]]
- `exterior.zones[shed_store_apron]` new: {"id": "shed_store_apron", "group": "rear", "polygon": [[-0.35, 25.35], [0.06, 25.35], [0.06, 26.7], [-0.35, 26.7]], "z": -0.42, "surface": "clay_block_paving_red_herringbone", "room": "shed"}
- `exterior.buildings[shed].outline`: [[-0.87, 23.4], [4.45, 23.4], [4.45, 28.9], [-0.87, 28.9]] -> [[-0.87, 25.02], [4.45, 25.02], [4.45, 30.75], [-0.87, 30.75]]
- `exterior.buildings[shed].roof.topZ`: 2.25 -> 2.4
- `exterior.buildings[shed].roof.polygon`: [[-0.87, 23.4], [4.45, 23.4], [4.45, 28.9], [-0.87, 28.9]] -> [[-0.87, 25.02], [4.45, 25.02], [4.45, 30.75], [-0.87, 30.75]]
- `exterior.buildings[shed].roof.verandaSoffitZ`: 1.83 -> 2.02
- `exterior.buildings[shed].roof.coping` new: {"sides": ["west", "rear", "east"], "width": 0.3, "topZ": 2.7}
- `exterior.buildings[shed].roof.fascia` new: {"z": [1.98, 2.2]}
- `exterior.buildings[shed].roof.gutterRimZ` new: 2.29
- `exterior.buildings[shed].roof.felt` new: {"frontZ": 2.3, "rearZ": 2.5}
- `exterior.buildings[shed].rooms[shed_workshop].polygon`: [[-0.6, 25.28], [4.18, 25.28], [4.18, 28.62], [-0.6, 28.62]] -> [[-0.6, 26.98], [4.18, 26.98], [4.18, 30.47], [-0.6, 30.47]]
- `exterior.buildings[shed].rooms[shed_workshop].ceilingZ`: 1.98 -> 2.13
- `exterior.buildings[shed].rooms[shed_store].polygon`: [[-0.77, 23.75], [-0.37, 23.75], [-0.37, 24.98], [-0.77, 24.98]] -> [[-0.77, 25.35], [-0.37, 25.35], [-0.37, 26.68], [-0.77, 26.68]]
- `exterior.buildings[shed].rooms[shed_store].ceilingZ`: 1.83 -> 2.02
- `exterior.buildings[shed].walls[shed_w_front].a`: [-0.87, 25.14] -> [-0.87, 26.84]
- `exterior.buildings[shed].walls[shed_w_front].b`: [4.45, 25.14] -> [4.45, 26.84]
- `exterior.buildings[shed].walls[shed_w_front].height`: 2.67 -> 2.82
- `exterior.buildings[shed].walls[shed_w_rear].a`: [-0.87, 28.76] -> [-0.87, 30.61]
- `exterior.buildings[shed].walls[shed_w_rear].b`: [4.45, 28.76] -> [4.45, 30.61]
- `exterior.buildings[shed].walls[shed_w_rear].height`: 2.67 -> 3.12
- `exterior.buildings[shed].walls[shed_w_west].a`: [-0.735, 23.4] -> [-0.735, 25.02]
- `exterior.buildings[shed].walls[shed_w_west].b`: [-0.735, 28.9] -> [-0.735, 30.75]
- `exterior.buildings[shed].walls[shed_w_west].height`: 2.67 -> 3.12
- `exterior.buildings[shed].walls[shed_w_east].a`: [4.315, 23.4] -> [4.315, 25.02]
- `exterior.buildings[shed].walls[shed_w_east].b`: [4.315, 28.9] -> [4.315, 30.75]
- `exterior.buildings[shed].walls[shed_w_east].height`: 2.67 -> 3.12
- `exterior.buildings[shed].walls[shed_w_store].a`: [-0.36, 23.75] -> [-0.36, 25.35]
- `exterior.buildings[shed].walls[shed_w_store].b`: [-0.36, 24.98] -> [-0.36, 26.68]
- `exterior.buildings[shed].walls[shed_w_store].height`: 2.25 -> 2.44
- `exterior.buildings[shed].openings[shed_w1].center`: [1.8, 25.14] -> [1.0, 26.84]
- `exterior.buildings[shed].openings[shed_w1].width`: 1.3 -> 2.0
- `exterior.buildings[shed].openings[shed_w1].sill`: 1.05 -> 1.09
- `exterior.buildings[shed].openings[shed_w1].height`: 1.0 -> 1.22
- `exterior.buildings[shed].openings[shed_d1].center`: [3.35, 25.14] -> [3.33, 26.84]
- `exterior.buildings[shed].openings[shed_d1].width`: 1.2 -> 1.69
- `exterior.buildings[shed].openings[shed_d1].height`: 2.08 -> 2.33
- `exterior.buildings[shed].openings[shed_w2].center`: [2.3, 28.76] -> [2.3, 30.61]
- `exterior.buildings[shed].openings[shed_store_doors].center`: [-0.36, 24.365] -> [-0.36, 26.02]
- `exterior.buildings[shed].openings[shed_store_doors].outsideZone`: "shed_veranda" -> "shed_store_apron"
<!-- diff:end -->

## (b) Surveyors' notes (garden, dims_envelope merged)

- **French doors**: white uPVC pair, each leaf one tall pane over a lower pane, mid-rail 0.93..1.06 above the threshold,
  brass levers at 1.11 (v11 f_0055, f_0194-0196); frame half a brick from the east wing wall. Not operated on camera:
  outward assumed.
- **Window W1**: two top-hung fanlights over one fixed pane, white cill. Brick between window and doors about 0.48 with
  the black doorbell at 1.25; 0.25 of brick east of the doors. Brick gauge here is **84 mm** (27.6 courses on the door
  jamb, 14.6 on the window jamb), not 75.
- **Veranda**: red block pavers in 45-degree herringbone with a SOLDIER course along the front edge; soffit Z 2.02 with
  its downlights. Furniture (bases): two folded teak chairs against the wall x 0.5..1.4; black pot (1.25, 25.8); two
  stone cat figures (1.75, 25.75); pine box x 1.6..2.3, y 26.1..26.5; grey mat 1.0 x 0.6 in front of the west leaf;
  softwood rack against the east wing wall x 3.85..4.20, y 25.25..26.60. Climber over the SW pier, store roof edge and
  west third of the fascia; bird box on the pier.
- **Store cupboard**: block about 1.0 wide; oxblood doors face east behind the front pier. The garden survey put the door
  plane at x 0.06; the verifier found 1 1/2 stretchers of brick between the window's west edge (x 0.00) and the doors, so
  the plane stays at -0.36 (-0.16..-0.36); shelves 0.40 deep on the west wall. The doors were hidden by the climber in
  round 3.
- From above (v13 t216): flat felt roof inside pale stone / concrete copings on the west, north and east parapets, white
  gutter along the south (veranda) edge (#C9C5B8 coping, #7D7E7A felt).
- Rear wall at 30.75 +/- 0.35 (weaker frames). Interior not filmed in round 3.

## (c) New footage

- **v11** f_0055 (t54, the front frontal), f_0194-0196; **v13** f_0211-0225 (roof and veranda from the Rose Room window).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

The building moved 1.62..1.85 north, and nothing in shed.py or shed_workshop.py followed it. See
`build/preview/shed_front_r3gate.jpg` and `shed_ws_door_r3gate.jpg`. Rebuild every position from the outline, the rooms
and the veranda zone, as the brief says.
- Crossing the new front wall (y 26.70..26.98) and the French doors `shed_d1` (x 2.485..4.175):
  - `shed.island` (x 0.31..2.75, y 26.28..27.52), with `.offcuts` and `.saws`
  - `shed.bench_east` (x 3.56..4.18, y 26.53..28.62), which goes through `shed.shed_d1.leaf.1` and its frame
- Room trim still on the old outline (x -0.60..4.18, y 25.28..28.62): `shed.cove` (z 1.91..1.98, at the old ceiling
  1.98; the new ceiling is 2.13) and `shed.skirting`. Both cross the store wall, the front wall and the door frame.
- Ceiling lights at the old ceiling height of 1.98:
  - `shed.downlight_trim.0`..`.2` (y 26.16..26.24) are now over the veranda or inside the front wall.
  - `shed.downlight_trim.3`..`.5` hang 0.15 below the new 2.13 ceiling.
  - `shed.ceiling_light` (x 3.23..3.47, y 25.68..25.92) is out over the veranda.
- On walls:
  - `shed.wall_rack` (x -0.60..-0.53, y 26.70..27.30) is in the west wall zone at the front.
  - `shed.switch` (x 4.165..4.18, y 25.477..25.563) is now outside, on the veranda wing wall.
- Workshop back. These are inside the workshop but 1.85 short of the new rear wall (y 30.47): `shed.bench_back` and
  `.machines` (y 28.0..28.62), `shed.racking` and `.items` (y 28.15..28.60), `shed.clamps` (y 28.5..28.62) and
  `shed.cnc` (x 3.63..4.13, y 27.26..28.32).
- Store. `shed.store.shelves` (x -0.77..-0.388, y 23.75..24.98) and `shed.store.contents` are still in the old place.
  They stand on the lavender bed and go through `garden.west_fence`. The store is now y 25.35..26.68.
- Veranda set, still at the old veranda (y 23.40..25.00). It is all on the lawn and path in front of the shed, at the
  old heights: the pieces that stood on the floor now float 0.03 above the ground.
  - `shed.chest` (x 2.04..2.61, y 24.47..24.84) and `shed.garden_furniture` (x 1.02..2.573, y 24.652..24.978)
  - `shed.stone_cats`, `shed.mat` and its edge, and `shed.doorbell` (y 24.97..25.0)
  - `shed.veranda_rack` and its bowls (x 3.80..4.20, y 23.42..24.37), and `shed.hook_rail` (x 4.128..4.22,
    y 23.60..24.85)
  - `shed.veranda_light_trim.0`..`.3` (z 1.825..1.83; the soffit is now 2.02) and `shed.soffit_boards.joints`
    (y 23.49..24.92, z 1.83)

  `shed.bird_box` (x -0.75..-0.57, y 23.255..23.40) now hangs on the west fence.
