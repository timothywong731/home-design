# bathroom2 - round-3 brief

Module `blender/rooms/bathroom2.py`. Decisions: `spec/RECONCILE3.md` (floor2a-01, -02, -03, -08, -09, -10; floor2b-01).

## (a) What moved in the shell

- **Room 0.16 shorter, from the south**: y 11.50..13.70 -> **11.66..13.70** (2.70 x 2.20 -> **2.68 x 2.04**), x 0.40..3.10 ->
  **0.42..3.10**. The north wall stays (13.70); the south wall (arch-wall line, 0.16 thick, faces 11.50 / 11.66) and the
  west (hall) wall (centreline 0.37) moved.
- **Door `d_bath2`**: 762 -> **686** leaf, centre y 11.951 -> **12.055**, clear y 11.71..12.40, hinge south, parks along
  the south wall; the opening starts 0.05 north of the tiled south wall.
- **Window `w_bath2`** centre y 12.48 -> **12.57** (reveal 12.25..12.89, its north jamb level with the cabin front);
  size unchanged; extReveal 0.06.
- Features: `bath2_pipe_boxing` x 2.98..3.10, y 11.50..12.16 -> **11.66..12.25**; `bath2_niche` unchanged (x 0.90..1.50 in
  the north wall); new **`bath2_shower_lining`** x 0.42..0.47, y 12.48..13.70, full height: the marble slab lining of the
  shower's west wall, 0.05 proud of the door wall with a mitred corner beside the door's north architrave (it carries the
  valve, riser and basket; not a pipe boxing).
- The wall to the Rose Room is a 0.14 partition (faces 13.70 / 13.84). Flank 0.35 thick outwards. Ceiling 2.47 (unchecked).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[bathroom2].polygon`: [[0.4, 11.5], [3.1, 11.5], [3.1, 13.7], [0.4, 13.7]] -> [[0.42, 11.66], [3.1, 11.66], [3.1, 13.7], [0.42, 13.7]]
- `rooms[bathroom2].size`: [2.7, 2.2] -> [2.68, 2.04]
- `walls[w_purple_n].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_purple_n].b`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_purple_n].thickness`: 0.3 -> 0.16
- `walls[w_hall_bath2].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_hall_bath2].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_neck_bath2].a`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_neck_bath2].b`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_bath2_study].a`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_bath2_study].b`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_bath2_study].thickness`: 0.45 -> 0.14
- `walls[w_flank_2_bath].a`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_flank_2_bath].b`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_flank_2_bath].thickness`: 0.3 -> 0.35
- `openings[d_bath2].center`: [0.35, 11.951] -> [0.37, 12.055]
- `openings[d_bath2].width`: 0.762 -> 0.686
- `openings[d_bath2].hingeAt`: [0.35, 11.57] -> [0.37, 11.71]
- `openings[w_bath2].center`: [3.25, 12.48] -> [3.275, 12.57]
- `openings[w_bath2].extReveal`: 0.01 -> 0.06
- `features[bath2_pipe_boxing].polygon`: [[2.98, 11.5], [3.1, 11.5], [3.1, 12.16], [2.98, 12.16]] -> [[2.98, 11.66], [3.1, 11.66], [3.1, 12.25], [2.98, 12.25]]
- `features[bath2_shower_lining]` new: {"id": "bath2_shower_lining", "level": "2", "type": "boxing", "room": "bathroom2", "polygon": [[0.42, 12.48], [0.47, 12.48], [0.47, 13.7], [0.42, 13.7]], "z": [6.02, 8.49]}
<!-- diff:end -->

## (b) Surveyors' notes (floor2_a, floor2_b, dims_vert merged)

Positions from the floor-tile lattice (v13 t103, t108, t123; 600 x 300 tiles) **in the room's local frame**: origin at the
room's SW corner (now world (0.42, 11.66)), x east, y north. The survey gave the room as 11.36..13.40; its local
positions are kept, which keeps the cabin's 0.055 to the north wall.

- Door clear y 0.05..0.74 (686 leaf, hinge south, parks along the south wall, free edge at x 0.69); towel radiator x
  0.76..1.29, z 0.20..1.80, matt black #191A1B; vanity x 1.33..1.92, plinth 0.30 deep, basin to about 0.45, rim 0.87; WC
  unit x 1.92..2.35, pan centre x 2.10-2.14, pan front y 0.69; tall cabinet x 2.35..2.68, y 0..0.30; tiled boxing on the
  east wall y 0.30..0.59; window reveal y 0.59..1.23; shower slab lining x 0..0.05 for y >= 0.82; tray about 1100 x 760,
  x 0.05..1.19, y 1.28..2.04; 0.07 strip; sauna x 1.26..2.62, y 1.23..1.98, 0.055 clear of the north wall and 0.06 of the
  window wall; bath mat 0.90 x 0.53 at x 0.31..1.22, y 0.73..1.26. (The survey's shower boxing was 0.12 deep: verified at
  0.04-0.05, slab build-up, v13 t108.5, t109.)
- Floor tiles 600 x 300, long side east-west, rows with irregular stagger (offsets 0.13-0.38), camera #C3C4C2.
- **Sauna cabin** 1.366 x 0.753 x 2.02 (maker's size; cabin depth checked from inside: 0.67 inside, 0.72-0.81 outside, v13
  t87): front = corner post and boarded panel about 0.62 (five boards, 100 face), glass door 0.60, post 0.13; capping 90
  high oversailing 20; base batten 45; grey glass door with two chrome hinges on the east edge, handle a vertical chrome
  cylinder dia 30 x 0.25 outside with a timber bar inside at z 1.0. Inside about 1.28 x 0.66: the bench runs the **whole
  depth along the east wall**, 0.50 wide, seven slats running north-south, top z 0.45 (the model has a small corner seat);
  three-slat backrest on the east wall z 0.80..1.10; one batten on the north wall above the bench at z 0.80; heater on the
  west wall at mid depth, 0.40 long x 0.25 deep, rocks at z 0.75, in a timber guard of two rails on posts; sliding timber
  vent 0.25 x 0.10 on the north wall at z 1.75, centre 0.40 from the NE corner (present 0.86); white slotted sensor 0.05 x
  0.08 on the east wall at z 1.80; round chrome-bezel thermometer on the front wall east of the door at z 1.75; coved
  timber fillets at the ceiling; dark grey floor mat about #6E6F6E; bucket and ladle on the bench (v13 f82-f105).
- Joinery: vanity doors shaker with flat recessed panels and dark bronze vertical bar handles 0.10 long (not V-grooved);
  the WC unit front has the vertical V-grooves; the tall cabinet side is a plain flat panel.
- Add: glass soap dish in a chrome ring left of the tap and a white double toothbrush holder right of it; antique-brass
  toilet-roll holder with a domed embossed hood (model chrome) under the sill; brushed steel toilet-brush cylinder; white
  square louvred extractor fan about 0.15 on the east wall above the window head (world y about 12.50, z 2.27).
- Shower: chrome rain head dia 0.25-0.30 on a swan-neck riser, black-faced hand shower, bar valve and wire basket on the
  slab-lined west face; sliding-leaf handle a square brushed bar 0.30; rail clamps to the fixed glass return beside the
  sauna.
- Window: reveal head and jambs white (not wall grey), marble-effect tiles return on both jambs to the dado line,
  fanlight handle brass-coloured; lower light fixed obscure glass, top-hung fanlight.
- Wall paint reads cooler than modelled: #BBC0C0 against the white ceiling at luminance 0.58, estimate #B5B8B8 (present
  #B9B7B1), low confidence. Ceiling 2.47 not measured this round.

## (c) New footage

- **v13** (PXL_20261121_132233957) **50-127**: basin, WC, tall cabinet, window, marble tiles, sauna interior, shower, towel
  rail.

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

What moved: the south wall from y 11.50 to 11.66, and the west face from x 0.40 to 0.42. `bath2_pipe_boxing` is now
y 11.66..12.25, and there is a new boxing `bath2_shower_lining` at x 0.42..0.47, y 12.48..13.70. `w_bath2` is now
y 12.25..12.89 (it was 12.16..12.80) and `d_bath2` y 11.712..12.398 (0.686 wide).
- South wall. Everything on it is 0.16 inside the wall; `build/preview/bathroom2_south_r3gate.jpg` shows the WC unit and
  vanity cut by it. Affected, all starting at y 11.50:
  - `bathroom2.vanity` and `.vanity.ends`; `bathroom2.basin`; `bathroom2.tap`, `.tap.water` and `.tap.lever`
  - `bathroom2.holders`, `.soapdish` and `.tumbler`
  - `bathroom2.mirror_cabinet` and its light; `bathroom2.picture`
  - `bathroom2.tallcab` with `.inside`, `.lower`, `.upper` and their pulls
  - `bathroom2.wc_unit` and `.wc_unit.top`
  - `bathroom2.towel_rail` and `.towel_rail.hooks`
  - `bathroom2.tile_trim`

  Move the run 0.16 north, and keep the tall cabinet clear of the pipe boxing (x 2.98..3.10, up to y 12.25).
- West wall. `bathroom2.screen`, `.screen.door`, `.shower`, `.shower.tray`, `.slab.n0`, `.slab.n1` and `.slab.w`
  (starting at x 0.40 or 0.41) are 0.01..0.02 inside the new 0.42 face. The shower (x 0.41..0.915, y 13.15..13.45) also
  cuts the face of the new shower lining at x 0.47. Rebuild the shower enclosure from x 0.47.
- Window. `bathroom2.sill` (x 3.07..3.33, y 12.161..12.82, z 6.821..6.85) and `bathroom2.plant` (y 12.182..12.763) are
  still on the old window: the south 0.09 runs into the reveal side (y 12.25) and the north end stops 0.07 short. Check
  `bathroom2.roll_holder` (x 2.98..3.10, y 12.388..12.526) against the boxing and the reveal.
