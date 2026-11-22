# blue_bedroom - round-3 brief

Module `blender/rooms/blue_bedroom.py`. Decisions: `spec/RECONCILE3.md` (dims_1-04, envelope-06, garden-22).

## (a) What moved in the shell

- **Entrance recess 0.07 wider**: recess east face x 0.40 -> **0.47** (recess 1.05 -> **1.12** x 0.43), on the corridor
  wall line; partition `w_recess_ensuite` on centreline 0.52.
- **Balcony door `d_balcony`** centre x 1.29 -> **1.255** (frame 1.62 wide, x 0.445..2.065), on one axis with the dining
  French doors and the Rose Room window. Re-fit anything keyed to the door (curtains, pelmet, head board).
- Flank wall 0.30 -> 0.35 thick outwards (inner face 3.10). Main room 3.75 x 3.91, ceiling 2.60 unchanged.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[blue_bedroom].polygon`: [[-0.65, 12.52], [0.4, 12.52], [0.4, 12.95], [3.1, 12.95], [3.1, 16.86], [-0.65, 16.86]] -> [[-0.65, 12.52], [0.47, 12.52], [0.47, 12.95], [3.1, 12.95], [3.1, 16.86], [-0.65, 16.86]]
- `walls[w_recess_ensuite].a`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_recess_ensuite].b`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_blue_s].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_ensuite_n].a`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_ensuite_n].b`: [3.25, 12.9] -> [3.275, 12.9]
- `walls[w_flank_1_blue].a`: [3.25, 12.9] -> [3.275, 12.9]
- `walls[w_flank_1_blue].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_1_blue].thickness`: 0.3 -> 0.35
- `walls[w_rear_1].b`: [3.25, 17.11] -> [3.275, 17.11]
- `openings[d_balcony].center`: [1.29, 17.11] -> [1.255, 17.11]
<!-- diff:end -->

## (b) Surveyors' notes (dims_1, dims_envelope merged)

- Ceiling 2.60 and cornice underside 2.52 confirmed (v3 t182.5, 4-point pose rms 2 px).
- d_blue leaf 762 x 1981, 0.155-0.18 from the leaf edge to the west wall, architrave 0.078 wide: present position stands.
- French doors (v3 t344.5, camera looking up): transom between 1.90 and 2.05, frame head 2.18-2.35 - not changed. From
  outside the balcony door frame is 1.62 wide, head Z 5.34, centred on the ground-floor French-door axis.
- Room length, bed size and balcony door width were not audited.

## (c) New footage

- Outside only: v13 207-225 (the balcony and its doors from the Rose Room window above), v11 188-196 (from the garden).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The west notch face moved from x 0.40 to x 0.47 (y 12.52..12.95). The switch cluster now floats 0.07 off it:
  `blue_bedroom.switch` (x 0.391..0.40, y 12.617..12.763, z 4.30..4.38) and `blue_bedroom.switch.chandelier`,
  `.switch.downlights` and `.switch.wall_light` (x 0.385..0.394). Move them to x 0.47.
- The curtains and pelmet (x 0.07..2.53) still cover `d_balcony`, which moved 0.035 west to x 0.505..2.005.
