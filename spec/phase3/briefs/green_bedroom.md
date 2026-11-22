# green_bedroom - round-3 brief

Module `blender/rooms/green_bedroom.py`. Decisions: `spec/RECONCILE3.md` (dims_1-01, -09; front-05; envelope-01, -02).

## (a) What moved in the shell

- **Ceiling 2.85 -> 2.77** above the floor 3.42 (Z 6.27 -> **6.19**); cornice underside **2.69**. The rear walls are 2.77
  high. Everything above the door heads was scaled to a 2.95 ceiling and should come down: door pediment shelf top about
  2.29 and apex about 2.48 above the floor (green_bedroom.md has 2.60), pelmets under the 2.69 cornice line.
- **Bay 0.05 west**: the square bay inside x 1.16..3.90 -> **1.11..3.85** (2.74 wide kept, depth 0.85 kept), on the axis
  of the window `w_green_bay` (centre x 2.53 -> **2.48**). Bay chamfers move with the corners.
- **Bay cheek walls thicker** (outside the bay is 3.48 wide, x 0.75..4.25): `w_bay_cheek_w_1` 0.26 -> **0.36** (faces
  0.75 / 1.11), `w_bay_cheek_e_1` 0.25 -> **0.40** (faces 3.85 / 4.25). Cheek windows: `w_green_cheek_w` x 1.03 ->
  **0.93** (wall centre), `w_green_cheek_e` x 4.025 -> 4.05; both keep y 0.43.
- East wall `w_east_1a` 0.23 -> 0.35 thick outwards (inner face 4.30 unchanged). Room 4.95 x 3.84 unchanged.
- Window heights unchanged: `w_green_bay` sill 0.70, height 1.85 (head 2.55), transom 2.00 (dims_1-09 rejected).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[green_bedroom].polygon`: [[-0.65, 0.99], [1.16, 0.99], [1.16, 0.14], [3.9, 0.14], [3.9, 0.99], [4.3, 0.99], [4.3, 4.83], [-0.65, 4.83]] -> [[-0.65, 0.99], [1.11, 0.99], [1.11, 0.14], [3.85, 0.14], [3.85, 0.99], [4.3, 0.99], [4.3, 4.83], [-0.65, 4.83]]
- `rooms[green_bedroom].ceilingZ`: 6.27 -> 6.19
- `walls[w_east_1a].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_east_1a].b`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_east_1a].thickness`: 0.23 -> 0.35
- `walls[w_front_1_w].b`: [1.03, 0.865] -> [0.93, 0.865]
- `walls[w_front_1_e].a`: [4.025, 0.865] -> [4.05, 0.865]
- `walls[w_front_1_e].b`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_bay_front_1].a`: [1.03, 0.01] -> [0.93, 0.01]
- `walls[w_bay_front_1].b`: [4.025, 0.01] -> [4.05, 0.01]
- `walls[w_bay_cheek_w_1].a`: [1.03, 0.01] -> [0.93, 0.01]
- `walls[w_bay_cheek_w_1].b`: [1.03, 0.865] -> [0.93, 0.865]
- `walls[w_bay_cheek_w_1].thickness`: 0.26 -> 0.36
- `walls[w_bay_cheek_e_1].a`: [4.025, 0.01] -> [4.05, 0.01]
- `walls[w_bay_cheek_e_1].b`: [4.025, 0.865] -> [4.05, 0.865]
- `walls[w_bay_cheek_e_1].thickness`: 0.25 -> 0.4
- `walls[w_green_rear].height`: 2.85 -> 2.77
- `walls[w_green_rear_e].b`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_green_rear_e].height`: 2.85 -> 2.77
- `openings[w_green_bay].center`: [2.53, 0.01] -> [2.48, 0.01]
- `openings[w_green_cheek_w].center`: [1.03, 0.43] -> [0.93, 0.43]
- `openings[w_green_cheek_e].center`: [4.025, 0.43] -> [4.05, 0.43]
- `features[green_bay].polygon`: [[1.16, 0.14], [3.9, 0.14], [3.9, 0.99], [1.16, 0.99]] -> [[1.11, 0.14], [3.85, 0.14], [3.85, 0.99], [1.11, 0.99]]
- `features[green_bay].chamfers`: [{"corner": [1.16, 0.99], "width": 0.12, "z": [3.42, 5.72], "stop": [5.72, 5.82]}, {"corner": [3.9, 0.99], "width": 0.12, "z": [3.42, 5.72], "stop": [5.72, 5.82]}] -> [{"corner": [1.11, 0.99], "width": 0.12, "z": [3.42, 5.72], "stop": [5.72, 5.82]}, {"corner": [3.85, 0.99], "width": 0.12, "z": [3.42, 5.72], "stop": [5.72, 5.82]}]
<!-- diff:end -->

## (b) Surveyors' notes (dims_1, front, dims_envelope merged)

- Ceiling: v3 t530.6, t532.5, v4 t94.5 (door-leaf scale) and v3 t546, t548 (sliding-door opening): cornice underside
  2.69-2.73, ceiling 2.76-2.82.
- Bay window heights: dims_1 read head 2.43 / transom 1.95 in v4 t12.5, but that 2.43 is the top of the fanlight glass;
  the frame head is at 2.52-2.54 and the transom 1.99-2.00 (v4 t20, t22) - present values stand. From the street the
  window frame reads Z 3.98..6.00 (low confidence; heads agree, the sill may be 0.14 lower) and the porch-side window
  `w_green_west` 4.20..6.14 against 4.20..6.00.
- From outside (v8 f20, f26, f131; v9 f12, f19): the window is centred in the bay; side lights are casements, the centre
  fixed with a trickle vent in the top light; mullion centres 0.58 in from each jamb, transom centre 5.44 world. The
  external bay is 3.48 against 2.74 inside: thick cheek walls (0.36-0.40) are the reconciliation; not settled.
- "Double wooden door" = the two separate single oak doors either side of the big wardrobe (v3 f_0523-0539), as
  modelled. Length 3.84, rear-wall chain, west window and bed size were not audited.

## (c) New footage

- Outside only: v8 13-66 and 114-138, v9 7-20 (the bay and the porch-side window from the street).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The ceiling dropped from 6.27 to 6.19, and the cornice is now z 6.09..6.19. These are now 0.08 above the ceiling:
  - `green_bedroom.downlight_trim.0`..`.7` (z 6.265..6.27): cannot be seen
  - `green_bedroom.rose` (z 6.221..6.27, centre (1.85, 2.85)): cannot be seen
  - the canopy of `green_bedroom.chandelier` (top 6.27): the fitting hangs from inside the slab
  - `green_bedroom.pelmets` (z 6.10..6.27)

  Lower them by 0.08 (use `ctx.ceil_z`).
- The bay moved 0.05 west (now x 1.11..3.85).
  - The east-side bay curtains cut into the east chamfer `green_bedroom.chamfer.green_bay.1`, the walls and the cornice:
    `green_bedroom.curtain.bay.closed.6` (x 2.52..3.88), `.closed.7` (x 3.797..3.858), `.open.2` (x 3.36..3.878),
    `.open.3` (x 3.80..3.888) and `green_bedroom.curtain.cords`.
  - The west drops `.closed.4` and `.open.0` stand 0.05 off the west bay face.

  Shift the bay set 0.05 west.
