# hall (vestibule + hallway) - round-3 brief

Modules `blender/rooms/vestibule.py`, `hallway.py`. Decisions: `spec/RECONCILE3.md` (porch-01..08, front-04, vert-02, vert-03, dimsG).

## (a) What moved in the shell

- **Vestibule is 0.13 longer**: 1.73 -> **1.86** between the thresholds (16.9 tile cells of 0.110). The inner screen
  (`w_screen_inner`, `d_inner`) moved from y 1.78 to **1.91** (faces 1.86 / 1.96); everything keyed to the screen or to
  the rear recess (keypad, switch, stool, lantern, sensor box) moves +0.13. The hallway's first segment absorbs it:
  front hall 3.22 -> **3.09** long (hallway now starts at y 1.96). Door plane and the main front wall did not move.
- **Front recess** y 0..0.74 -> **0..0.99**; piers and basket vault 0.74..1.29 -> **0.99..1.44** (pier depth 0.45 kept);
  rear recess 1.44..1.86.
- **East side of the front recess**: the bay's west cheek wall now has its vestibule face at x **0.75** (was 0.90). The
  wall `w_bay_cheek_w` is 0.28 thick (faces 0.75 / 1.03), centre x 0.89. There is **no front-wall return** beside the
  door: the uPVC frame stands in the corner. The east pier stands 0.20 proud of the cheek wall (0.10 proud of the rear
  recess wall).
- **Street door `d_street`**: leaves 1.18 -> **1.26** (2 x 0.63), frame 1.24 -> **1.39** (x -0.67..0.72, from the party
  wall to the cheek wall), centre x 0 -> 0.025; leaf / head height 2.03 -> **1.95**; transom glass 2.12-2.50 and frame
  top 2.57 unchanged (all one glazing-bar scale, P = 0.24).
- **Front-recess ceiling**: the two 45-degree haunches are deleted. New feature `vest_ceiling_slope` (type
  `ceiling_haunch`, wallAt y 0): a panel rising from **2.62 at the door head (y 0) to the flat 2.85 at y 0.62**, soft
  crease, flat 2.85 to the arch wall. Both downlights sit in the sloping panel. East edge coved r 0.12 onto the cheek
  wall, west edge sharp. No cornice.
- **Cheek light `w_bay_cheek_w`**: centre (1.00, 0.37) w 0.50 -> **(0.89, 0.63) w 0.45**; north architrave 0.05 from the pier.
- **Hall arch `a_hall` / `hall_arch`**: springing 2.40 -> **2.08**, crown 2.75 -> **2.55**, now a plain semicircle on the
  0.94 span (the three-centred `haunch` 0.32 is removed); corbels z 2.02-2.40 -> **1.75-2.08** (height 0.33).
- **Rear corridor ceiling** (y 9.03..12.23, x -0.65..0.45): 2.84 -> **2.70** (new ceiling zone `rear_corridor`); the strip
  y 8.13..9.03 keeps 2.84 (not measured). Pilasters: `hall_pilaster_n` top 2.70, `hall_pilaster_s` top 2.84.
- Main flight now 14 risers of 0.2036 (see `stairs.md`): the hall-side spandrel, string and dado rake follow (rake 1.37).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[vestibule].polygon`: [[-0.65, 0], [0.9, 0], [0.9, 0.74], [0.65, 0.74], [0.65, 1.73], [-0.65, 1.73]] -> [[-0.65, 0], [0.75, 0], [0.75, 0.99], [0.65, 0.99], [0.65, 1.86], [-0.65, 1.86]]
- `rooms[vestibule].size`: [1.3, 1.73] -> [1.3, 1.86]
- `rooms[hallway].polygon`: [[-0.65, 1.83], [0.65, 1.83], [0.65, 5.05], [0.15, 5.05], [0.15, 7.68], [0.99, 7.68], [0.99, 8.73], [0.45, 8.73], [0.45, 12.23], [-0.65, 12.23]] -> [[-0.65, 1.96], [0.65, 1.96], [0.65, 5.05], [0.15, 5.05], [0.15, 7.68], [0.99, 7.68], [0.99, 8.73], [0.45, 8.73], [0.45, 12.23], [-0.65, 12.23]]
- `rooms[hallway].size`: [1.3, 10.4] -> [1.3, 10.27]
- `rooms[hallway].ceilingZones[rear_hall].polygon`: [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.45, 8.73], [0.45, 12.23], [-0.65, 12.23]] -> [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.45, 8.73], [0.45, 9.03], [-0.65, 9.03]]
- `rooms[hallway].ceilingZones[rear_corridor]` new: {"id": "rear_corridor", "polygon": [[-0.65, 9.03], [0.45, 9.03], [0.45, 12.23], [-0.65, 12.23]], "z": 2.7}
- `walls[w_party_w_vest].b`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_party_w_hall].a`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_front_vest].b`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_bay_cheek_w].a`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_bay_cheek_w].b`: [1.0, 0.865] -> [0.89, 0.865]
- `walls[w_bay_cheek_w].thickness`: 0.2 -> 0.28
- `walls[w_front_nib_w].b`: [1.1, 0.865] -> [1.03, 0.865]
- `walls[w_screen_inner].a`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_screen_inner].b`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_vest_living].b`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_hall_living].a`: [0.725, 1.78] -> [0.725, 1.91]
- `openings[d_street].center`: [0, -0.06] -> [0.025, -0.06]
- `openings[d_street].width`: 1.18 -> 1.26
- `openings[d_street].height`: 2.03 -> 1.95
- `openings[d_inner].center`: [0, 1.78] -> [0, 1.91]
- `openings[a_hall].height`: 2.75 -> 2.55
- `openings[a_hall].springing`: 2.4 -> 2.08
- `openings[a_hall].crown`: 2.75 -> 2.55
- `openings[w_bay_cheek_w].center`: [1.0, 0.37] -> [0.89, 0.63]
- `openings[w_bay_cheek_w].width`: 0.5 -> 0.45
- `features[vest_pier_w].polygon`: [[-0.65, 0.74], [-0.55, 0.74], [-0.55, 1.29], [-0.65, 1.29]] -> [[-0.65, 0.99], [-0.55, 0.99], [-0.55, 1.44], [-0.65, 1.44]]
- `features[vest_pier_e].polygon`: [[0.55, 0.74], [0.65, 0.74], [0.65, 1.29], [0.55, 1.29]] -> [[0.55, 0.99], [0.65, 0.99], [0.65, 1.44], [0.55, 1.44]]
- `features[vest_vault].polygon`: [[-0.55, 0.74], [0.55, 0.74], [0.55, 1.29], [-0.55, 1.29]] -> [[-0.55, 0.99], [0.55, 0.99], [0.55, 1.44], [-0.55, 1.44]]
- `features[hall_pilaster_s].z`: [0, 2.95] -> [0, 2.84]
- `features[hall_pilaster_n].z`: [0, 2.95] -> [0, 2.7]
- `features[hall_arch].springing`: 2.4 -> 2.08
- `features[hall_arch].crown`: 2.75 -> 2.55
- `features[hall_arch].haunch` removed (was 0.32)
- `features[hall_arch].corbelSize.height`: 0.38 -> 0.33
- `features[hall_arch].corbelSize.z`: [2.02, 2.4] -> [1.75, 2.08]
- `features[vest_haunch_w]` removed
- `features[vest_haunch_e]` removed
- `features[vest_ceiling_slope]` new: {"id": "vest_ceiling_slope", "level": "G", "type": "ceiling_haunch", "room": "vestibule", "polygon": [[-0.65, 0], [0.75, 0], [0.75, 0.62], [-0.65, 0.62]], "z": [2.62, 2.85], "wallAt": 0.0}
<!-- diff:end -->

## (b) Surveyors' notes (porch, front, dims_G, dims_vert merged)

**Street door set** (v9 f_0005-0007, f_0013, f_0017-0020, f_0043-0048, f_0059-0060; v8 f_0104-0108; photo). White uPVC
#F4F4F0. Per leaf: glazing 0.41 x 0.94 at z 0.865..1.80, **3 wide x 4 high** obscure stippled lights (not 3 x 3), 16 mm
bars inside the unit, 20 mm beads; hinge stile 0.095, meeting stile 0.125, top rail 0.105, mid-rail z 0.72..0.865; lower
flat panel with a raised moulding frame 0.46 x 0.62 at z 0.10..0.72. Transom bar zone up to 2.12, plain frosted transom
light (never the lettering), top member to 2.57. Brass lever on a 0.24 x 0.03 backplate on both leaves at the meeting
stiles, both faces (spindle about 0.95, cylinder 0.09 below, 0.055 from the meeting edge); brass letter plate 0.30 x
0.07 on the west leaf's mid rail; three white flag hinges per leaf on the outer jambs (covers 0.115 x 0.035 x 0.03 at z
0.20 / 0.97 / 1.70); white contact sensors on the east jamb at z 0.25 and 1.45; four small white caps along the
transom bead. Both leaves open outward (about 100 deg). Threshold: aluminium strip on a white cill (#E0DED8), upstand
0.03 inside, cill face 0.06-0.07 above the setts. (The porch survey worked at P = 0.232, i.e. 4 % smaller: scale its
z values by 1.035.)

**Cheek wall (x 0.75)**: two lights, glass about 0.45 wide, lower z 0.62..1.80, upper 1.97..2.46, each with a 75 mm
moulded white architrave, a splayed lining about 0.05 deep and a dark 15 mm gasket line. Dado (top 0.965, as
in the hall) and skirting run on the cheek wall from the lower light's architrave to 0.04 short of the door
corner, with returned ends; two white vertical cover strips in the corner (flat 0.07 + beaded 0.035).
`vestibule.door_corner` builds dado and skirting on a 0.28 front-wall return that does not exist: replace it by that stub
and the strips.

**Tiles**: blue-square rows centred y 0.155, 0.486, 0.817, 1.148, 1.479, 1.810 (pitch 0.331, 3 cells) with two dark rows
between; a dark row cut to 0.9 cell at the street threshold; a full blue row at the inner sill. Columns of blue squares
about x -0.425, -0.095, 0.235, 0.565 (low confidence). Dark cells charcoal, keep #2E2E30.

**Vestibule furnishing**: downlights side by side in the sloping panel at about (-0.30, 0.30) and (0.32, 0.30), z about
2.69 (on the slope), white bezel 0.085-0.09 (v9 t31.5, v2 f_0915) - now at (-0.25, 0.28) / (0.35, 0.50). Door mat 0.60 x
1.10 at x -0.44..0.16, y 0.04..1.14 (its north end beside the pier, third pattern row from the inner sill; v1 t25, v9
t57). Alarm keypad about 0.16 x 0.11, blank face, no logo (v2 t903.2). Keypad, switch, stool and lantern keep their
offsets from the inner screen and the rear recess's east wall (+0.13 now); lantern at the centre of the rear recess, y
about 1.65. Optional: honey four-tier slatted shoe rack 0.70 x 0.27 x 0.75 against the cheek wall under the lower light
(x 0.45..0.72, y 0.05..0.75). Leave out coats, umbrellas, shoes. `CANOPY_Z = 2.62` in vestibule.py follows the flat
soffit, which is now raked (see `envelope.md`).

**Hallway**: small white sensor box about 0.06 x 0.09 on the hall's west wall just north of the inner frame, z about
2.25 (v9 f_0029-0030). Inner doors, arch, imposts and archivolt (band about 0.15 with an outer roll, v9 f_0029-0031)
confirmed, no change. Inner mahogany frame top z 2.82 +/- 0.04 (v6 t42). Front hall 1.30 and corridor 1.10 stand.
Oak boards run along Y at **0.24 pitch** (not 0.22): across the front hall five full boards plus cut boards, joints at
0.13, 0.38, 0.62, 0.86, 1.11 from the west skirting (v2 t682.6); the same joint lines continue into the corridor.
Hall-side dining door architrave white, about 0.07. Front hall ceiling 2.95 confirmed (v1 t778, cornice wall edge 2.76).
Dado top 0.97 confirmed at the kitchen leaf (v1 t744). Wall below the dado reads darker and warmer than modelled (same
paint as the second-floor hall, estimate #C0B9AD against #C8C5BB: change both or neither).

**Arch between lobby and rear corridor** (y 8.88): each corbel is three parts - moulded shelf, top 2.08, roughly level
with the top of the open kitchen leaf; a scroll under it to about 1.85; a small drop to about 1.75 (v6 t50, t303.1; v1
t744; v2 t514.8, t515.6). Only about 0.15 of wall remains above the crown on the corridor side; the corridor cornice
lower edge reads 2.60-2.67 on its end wall (v2 t514.8). The lobby strip west of x 0.15 carries the smoke alarm and
downlights on a higher ceiling than the soffit over x > 0.15 (dentil cornice along x 0.15, v1 t752); its height is not
settled (2.59, 2.75 or 2.95). `lib/mouldings.py` draws the corridor cornice on zone `rear_hall`, which now stops at
y 9.03: the corridor part is zone `rear_corridor` (request to the mouldings owner).

## (c) New footage

- v9 (PXL_20261121_124601813) 1-6 out through the open door; 7-20 porch and door from the forecourt; **21-44 vestibule
  interior** (inner doors, transom, ceiling, side lights, glazing); 45-58 outside of the door, side lights, canopy.
- v8 (PXL_20261121_124142138) 102-113 path to the door; 104-108 door from outside; 114-138 canopy from below.
- Photo `reference/photos/vestibule_front_door_open.jpg` (door leaf, transom, shoe rack, tiles).
- No new footage of the hallway itself (dims_G / dims_vert re-measured v1, v2, v6).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- `vestibule.door_corner` (x 0.62..0.90, y -0.02..0.03, z 0..2.60) now stands 0.15 inside the cheek wall: the vestibule
  east face is x 0.75 for y 0..0.99. It also cuts through the new street-door frame `vestibule.d_street.frame` (101
  triangles). Remove it: joinery now builds `vestibule.d_street.cover` (shell request).
- `vestibule.stool` and its lid and drawers (x 0.196..0.624, y 1.326..1.694, z 0.26..0.50) run into `vest_pier_e`. The
  pier moved to x 0.55..0.65, y 0.99..1.44, so they overlap over x 0.55..0.624, y 1.326..1.44. Move the stool north of
  y 1.44 (the bay between the piers and the inner doors is now y 1.44..1.86) or west of x 0.55.
- `vestibule.lantern` (canopy at z 2.85; body x -0.098..0.098, y 1.371..1.589) straddles the north end of `vest_vault`
  (y 0.99..1.44, crown 2.66). Its canopy and rod cut the vault end face at y 1.44 between z 2.66 and 2.85. Centre it in
  the flat-ceiling bay y 1.44..1.86 (about y 1.65).
- Porch downlights `vestibule.outside_trim.0`, `.1` and `.2` and their lamps (x -0.425..0.425, y -0.385..-0.295,
  z 2.615..2.62) are now about 0.10 inside the canopy and cannot be seen. The soffit is now raked:
  `envelope.porch_soffit_z(y)` = 2.63 + 0.5349 (y + 0.12), which is 2.512 at y -0.34.
- The inner doors moved to y 1.91 (they were at 1.78). `vestibule.keypad` (y 1.445..1.595) and `vestibule.switch`
  (y 1.477..1.563) on the x 0.65 face are not broken; check them against the survey.
- Hallway: nothing broken. The downlights and the Wi-Fi access point followed the 2.70 ceiling.
