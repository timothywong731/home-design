# dining - round-3 brief

Module `blender/rooms/dining.py`. Decisions: `spec/RECONCILE3.md` (dimsG-01, dimsG-02, envelope-03, -06, -07).

## (a) What moved in the shell

- **West wall 0.06 east**: room face x -0.65 -> **-0.59** (in the plane of the hall pilaster). `w_party_w_dining` 0.23
  -> 0.29 thick, centre -0.765 -> -0.735, party-line face -0.88 unchanged. Room 3.75 -> **3.69** x 4.50. Everything keyed
  to the west wall moves +0.06 in x (`X0 = -0.65` in dining.py and the west-wall decor). `d_dining` does not move.
- **Ceiling 2.80 -> 2.62**; the four dining walls are 2.62 high; `dining_chimney_breast` z 0..2.62. The cornice lower
  edge belongs at **Z 2.53**: that needs `cornice_dining` (lib/mouldings.py) reduced from a 0.15 drop to about 0.09
  (projection about 0.12) - requested from the mouldings owner. Until then the lower edge lands at 2.47. The north-wall
  pelmet (was 2.50-2.65) must end under 2.53; the crest plaques (about 0.22 high) fill the band between the doorcase cap
  top (2.22) and the cornice.
- **North wall re-spaced** on one axis x **1.255** (the room centre now that the west face is -0.59): `d_french` 1.225 ->
  1.255 (fanlight head 2.35); side windows `w_dining_n_w` -0.09 -> **-0.185** and `w_dining_n_e` 2.54 -> **2.695**
  (axes +/-1.44 from the doors), both 0.52 -> **0.65** wide, height 1.83 -> **2.00** (frame head 2.37), transom 1.40 ->
  **1.32**, sill 0.37 kept. Recess features `dining_n_recess_w / _door / _e` follow (x -0.51..0.14, 0.66..1.85, 2.37..3.02).
  The side windows now sit 0.08-0.11 from the room corners, as filmed.
- Flank wall 0.30 -> 0.35 thick outwards (inner face 3.10 unchanged); east windows `w_dining_e_s / _e_n` get extReveal 0.15.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[dining].polygon`: [[-0.65, 12.36], [3.1, 12.36], [3.1, 16.86], [-0.65, 16.86]] -> [[-0.59, 12.36], [3.1, 12.36], [3.1, 16.86], [-0.59, 16.86]]
- `rooms[dining].ceilingZ`: 2.8 -> 2.62
- `rooms[dining].size`: [3.75, 4.5] -> [3.69, 4.5]
- `walls[w_party_w_dining].a`: [-0.765, 12.295] -> [-0.735, 12.295]
- `walls[w_party_w_dining].b`: [-0.765, 17.11] -> [-0.735, 17.11]
- `walls[w_party_w_dining].thickness`: 0.23 -> 0.29
- `walls[w_party_w_dining].height`: 2.8 -> 2.62
- `walls[w_flank_dining].a`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_flank_dining].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_dining].thickness`: 0.3 -> 0.35
- `walls[w_flank_dining].height`: 2.8 -> 2.62
- `walls[w_dining_s_utility].b`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_dining_s_utility].height`: 2.8 -> 2.62
- `walls[w_dining_n].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_dining_n].height`: 2.8 -> 2.62
- `openings[d_french].center`: [1.225, 17.11] -> [1.255, 17.11]
- `openings[d_french].transom.height`: 2.32 -> 2.35
- `openings[w_dining_n_w].center`: [-0.09, 17.11] -> [-0.185, 17.11]
- `openings[w_dining_n_w].width`: 0.52 -> 0.65
- `openings[w_dining_n_w].height`: 1.83 -> 2.0
- `openings[w_dining_n_w].transomBar`: 1.4 -> 1.32
- `openings[w_dining_n_e].center`: [2.54, 17.11] -> [2.695, 17.11]
- `openings[w_dining_n_e].width`: 0.52 -> 0.65
- `openings[w_dining_n_e].height`: 1.83 -> 2.0
- `openings[w_dining_n_e].transomBar`: 1.4 -> 1.32
- `openings[w_dining_e_s].center`: [3.25, 13.02] -> [3.275, 13.02]
- `openings[w_dining_e_s].extReveal` new: 0.15
- `openings[w_dining_e_n].center`: [3.25, 16.2] -> [3.275, 16.2]
- `openings[w_dining_e_n].extReveal` new: 0.15
- `features[dining_chimney_breast].z`: [0, 2.8] -> [0, 2.62]
- `features[dining_n_recess_w].polygon`: [[-0.34, 16.86], [0.18, 16.86], [0.18, 17.24], [-0.34, 17.24]] -> [[-0.51, 16.86], [0.14, 16.86], [0.14, 17.24], [-0.51, 17.24]]
- `features[dining_n_recess_door].polygon`: [[0.64, 16.86], [1.83, 16.86], [1.83, 17.24], [0.64, 17.24]] -> [[0.66, 16.86], [1.85, 16.86], [1.85, 17.24], [0.66, 17.24]]
- `features[dining_n_recess_e].polygon`: [[2.295, 16.86], [2.815, 16.86], [2.815, 17.24], [2.295, 17.24]] -> [[2.37, 16.86], [3.02, 16.86], [3.02, 17.24], [2.37, 17.24]]
<!-- diff:end -->

## (b) Surveyors' notes (dims_G, dims_envelope, dims_vert merged)

- Ceiling: three frames read the cornice lower edge at 2.51-2.54 (v2 t27.0 homography on the 0.838 x 1.981 leaf; v1
  t741 cross-ratio; v1 t719 dado scale) and the cornice ceiling line only 0.13-0.14 above it, so ceiling 2.62 +/- 0.04.
  The dims_vert survey read 2.75 +/- 0.05 from v1 t740 with a level-camera assumption; the stair rise (2.85 landing) does
  not depend on it any more (14 risers, see stairs.md).
- West corner: the dark doorcase stands tight in the SW corner, about 0.015 between its west architrave and the west
  wall; the west-wall dado rail and skirting start at the architrave (v2 t26.3, t24.2, t27.0; v1 t740-741).
- Door leaf 0.838 x 1.981 confirmed; dark architraves 0.085 wide each side (model note says 0.10); cap underside 2.08,
  top 2.22. Dado rail top 1.047, rail 0.045 deep; skirting top 0.18 (dims_vert reads the dado at about 0.96 with a level
  camera in v1 t740 - not pursued).
- 3-gang plate 0.146 x 0.086, centre about (0.64, 12.36, 1.35) (spec x 0.67).
- TV: bottom edge 1.13, top 2.11, west edge x 0.89: 0.98 high suggests about 1.74 wide rather than 1.89, but its east
  edge was not seen - check before changing.
- Boards run along Y at 0.24 pitch (3.36 boards across the 0.838 leaf at the threshold).
- From outside: the three north openings are symmetric about the French-door axis, side windows tucked into the room
  corners (also v2 f_0140, v1 f_0694); outside frames 0.60-0.67 wide, side-window heads 2.37, transoms 1.32; French unit
  1.19 wide, leaf head 1.97, fanlight head 2.35. Outside the axis measures 2.34 from the flank corner (x 1.11), inside the
  symmetric screen and the Rose Room mullion put it at 1.25-1.27: adopted 1.255, open question.
- East windows outside: reveal 0.18, stone sill block top z 0.97, 0.10 thick, 0.06 longer than the opening each side
  (v11 t26, t176-t182).

## (c) New footage

- No new interior footage. Exterior: v11 18-60 and 154-187 (east windows from the side passage), v13 207-225 (rear wall
  and French doors from above).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The west wall moved 0.06 east (face x -0.65 -> -0.59). Everything hung on it is now inside the wall and cannot be seen
  (`build/preview/dining_west_r3gate.jpg` shows a bare wall). Move these to x -0.59:
  - `dining.mirror` (x -0.65..-0.609, y 13.90..15.37)
  - `dining.carved_panel.0` (y 13.29..13.73) and `dining.carved_panel.1` (y 15.50..15.94), both x -0.65..-0.605
  - all 28 crest plaques `dining.plaque.w.0`..`.27` (x -0.65..-0.618)
  - `dining.socket.2` (y 16.277..16.423, z 0.357..0.443)

  The back of `dining.door_stop` (x -0.63..-0.468, y 13.00) is 0.04 inside the wall.
- The ceiling dropped from 2.80 to 2.62, and the cornice is now z 2.47..2.62. The chandelier and downlights followed;
  the crest frieze did not. `dining.plaque.s.0`..`.7` (y 12.36, z 2.41..2.59) and `dining.sword` (x 1.02..2.26,
  z 2.32..2.54) cut into `dining.cornice`, and so would the upper row of west plaques (z 2.41..2.605). Drop the frieze
  below 2.47, and lower the lower row (z 2.18..2.36) to match.
- The north windows are wider and taller: `w_dining_n_w` x -0.51..0.14, `w_dining_n_e` x 2.37..3.02, head 2.37.
  - The crown of `dining.citrus` (x 2.254..3.031, y to 17.00, z to 1.81) now pokes 0.14 into the wall pier west of
    `w_dining_n_e` (over x 2.25..2.37, z 1.70..1.82).
  - `dining.curtain.cords.0` (x 0.081..0.108), `dining.curtain.cords.1` (x 2.364..2.391) and the open stacks
    `dining.curtain.0` (x 0.11..0.71) and `dining.curtain.1` (x 1.762..2.363) overlap the widened windows by 0.02..0.03.
  - `dining.curtain.track` (x 0.08..2.393, z 2.486..2.50) is now in the cornice band (z 2.47..2.62); check it.
