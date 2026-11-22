# Phase 3 — dimension audit, ground floor interior (`dims_G`)

Surveyor notes for vestibule, hallway, living, dining, kitchen, utility, wc. World frame of `spec/BRIEF.md`.
Frames are written `v2 t=26.27` (full-resolution still at that second of the video; 1 fps frame file = t + 1).
Scratch (private): stills, crops and overlays in `reference/work/r3_dims_G/`, scripts in `build/r3/dims_G/`
(`grab.py` sharpest frame in a time window, `meas.py` line snapping / vanishing points / plane metrology,
`autovp.py`, `joints.py`, `m_*.py` one script per measurement).

**Read this first: how much was covered.** The audit asked for every room, door and window. I did not get
that far. What is below is measured; everything in section 5 is *not* re-measured and keeps its present
evidence. No model preview was rendered; the model was read from `spec/house.json` and `spec/plan_G.png` only.
Footage looked at: contact sheets of v2 (sheets 1-3, 6-16), v6 (1-2), v7, v9 (1), v10 (1), v1 (sheet 10); about
25 full-resolution stills of v1 / v2 / v6; the vestibule photo. v9 and v10 added nothing measurable for the
ground-floor shell (v10 is table-top close-ups; v9's vestibule frames look up at the vault with no floor
reference in the same frame).

## 1. Method and its limits

- **Camera.** The videos are the phone's ultrawide lens, already rectilinear (a 500 px dado edge running to
  x = 1060 fits a straight line to 0.5 px rms). Focal length from vanishing points: orthocentre solutions 889,
  890, 890, 906 px on four stills of v2 / v6 (two more gave 777 and 1006 with one vanishing point near
  infinity); two-point solutions with the principal point at the centre 815-877. Use **f = 870 +/- 40 px at
  1080 x 1920**, as RECONCILE D3 found. The orthocentres sit near (530, 1080), not (540, 960): the principal
  point is uncertain by about 100 px vertically (stabilisation crop). The photo is the same lens at 12 mm
  equivalent: f = 1390 +/- 30 px at 3072 x 4080.
- **What is reliable:** (a) counts of floor boards and tiles; (b) ratios inside one wall plane scaled from a
  door leaf in that plane, where the result does not move with f (tested 800-940 px and both principal
  points); (c) heights along one vertical line by cross-ratio from the floor, a 1.981 leaf top and the
  vertical vanishing point.
- **What is not:** distances along the floor away from the camera in a single frame. In v2 t=682.63 the
  same solution that puts the stair bullnose 2.2-2.5 m from the inner doors also makes the living-room
  doorcase 0.65 m wide (it is at least 0.90) and returns a camera height anywhere from 0.56 to 1.45 m
  depending on which constraints are used. Such figures move 10-15 % with the principal point. **I therefore
  could not improve any length along Y in the hall**, and no change to the Y chain is proposed.
- Line picking: rough picks snapped to LSD segments (`meas.Im.seg`). My first gradient-snapping version put
  the vertical vanishing point of v2 t=682.63 at y 2596 instead of 2170; figures from it are not used.
- One reading was withdrawn after a second frame (section 3, living chamfer): a wall strip beyond a proud
  architrave is partly hidden in a grazing view. Single-frame readings below are marked as such.

## 2. Dimension table

`=` confirmed within tolerance, `!` differs by more than tolerance (change proposed), `?` differs, not settled.

| # | item | house.json | present | measured | method, frames | conf | |
|---|---|---|---|---|---|---|---|
| 1 | dining door leaf width | `d_dining.width` | 0.838 | **0.838 +/- 0.005** | leaf aspect in its own plane, height 1.981; v2 t=26.27; 0.835-0.840 for f 830-960 | high | = |
| 2 | dining door architrave, dining side | notes | 0.10 dark | 0.085 each side (0.081 W, 0.085 E) | same plane | high | = |
| 3 | dining doorcase cap | notes "to 2.20" | 2.20 | bottom 2.08, top **2.22** | same plane | high | = |
| 4 | dining cornice lower edge | `rooms.dining.ceilingZ` 2.80 (dining.md: cornice bottom 2.65) | 2.65 | **2.55 +/- 0.03** (2.547 at the leaf's east edge, 2.574 at its west edge; plain cross-ratio 2.53) | door plane, leaf 1.981, v2 t=26.27; scale checked in the same still on the 3-gang plate (0.084 x 0.141 for 0.086 x 0.146) and the skirting (0.18) | high for the cornice edge | ! |
| 5 | dining ceiling | `rooms.dining.ceilingZ` | 2.80 | **2.70 +/- 0.05** = cornice edge + the 0.15 drop of dining.md; 2.66 if the drop is 0.10 | as 4; dining.md section 10 already noted "a socket-plate scale suggests ~2.6" from v1 F_741 | medium | ! |
| 6 | dining west wall face | `rooms.dining.polygon` west edge | x -0.65 | **x -0.59 +/- 0.02**: wall 0.10 west of the leaf's west edge (architrave 0.085 + 0.015 gap; up to 0.012 more hidden behind the architrave) | door plane v2 t=26.27; seen again v2 t=24.20: the dark architrave and its cap stand tight in the corner and the west-wall dado rail starts at the architrave | medium | ! |
| 7 | dining width | `rooms.dining.size[0]` | 3.75 | 3.69 follows from 6 with the east wall kept; not measured across | TV chain on the south wall gives 3.55-3.70 (TV size unknown) | low | ? |
| 8 | dining dado / skirting | room spec | - | dado top 1.047, bottom 1.003; skirting top 0.18 | door plane v2 t=26.27 | high | n/a |
| 9 | dining 3-gang switch | dining.md 0.67 | x 0.67 | centre x 0.64, z 1.35 (plate z 1.305-1.389, west edge 0.21 east of the leaf) | door plane | high | = |
| 10 | dining TV | dining.md | x 0.86-2.75 | west edge x 0.89; bottom 1.13, top 2.11 (0.98 high, so nearer 78-80 in than 85 in) | door plane; east edge not in frame | medium | ? |
| 11 | floor board pitch (hall, dining) | room specs "about 220" | 0.22 | **0.243 +/- 0.006**: 0.238 from 5.27 boards across the front hall taken as 1.26 between skirtings; 0.249 from 3.36 boards across the 0.838 dining leaf | board joints as LSD families in the rectified floor, v2 t=682.63; joints at the door line, v2 t=26.27 | medium | n/a |
| 12 | front hall width | `rooms.hallway.polygon` | 1.30 | 5.27 boards = 1.28 +/- 0.03 + skirtings = **1.32 +/- 0.04** | 11; and frame width / leaf height in v6 t=42.03 agrees with the 610 leaves | medium | = |
| 13 | rear corridor width (north end) | `rooms.hallway.polygon` | 1.10 (1.04 at the pilaster) | 4.43-4.62 boards = 1.08-1.12 between skirtings = 1.12-1.16 | v2 t=670.97, east skirting hidden by the open utility door | low-medium | = / ? |
| 14 | front hall : corridor width ratio | - | 1.18 | 5.27 / 4.5 = 1.17 | same joint lines run the whole hall | medium | = |
| 15 | inner frame top | `d_inner.transom.height` 2.79, notes 2.83 | 2.83 | **2.82 +/- 0.04** | vertical cross-ratio, leaf 1.981, v6 t=42.03 | medium | = |
| 16 | front hall ceiling | `rooms.hallway.ceilingZ` | 2.95 | 2.87-2.92 (frame top + 0.05-0.10 to the ceiling line) | same still | low | = |
| 17 | rear corridor cornice lower edge | `ceilingZones.rear_hall` 2.84 | - | 2.67 +/- 0.06 at the end wall, so ceiling about 2.84 with a 0.17 cornice | vertical cross-ratio on the dining door jamb, v2 t=514.83 | medium | = |
| 18 | living: wall between door architrave and NW chamfer | polygon vertex (0.80, 4.78) | 0.24 | 0.20 +/- 0.04 (0.21-0.25 from the 146 mm socket plate on the chamfer, v2 t=718.43; 0.16-0.19 after occlusion correction, v2 t=790.50) | two frames | medium | = |
| 19 | living chamfer face | `living_nw_chamfer` | 0.58 | 0.52-0.58 | socket plate, v2 t=718.43 | medium | = |
| 20 | kitchen floor tile width | kitchen.md "about 200 x 1200" | 0.20 | **0.245 +/- 0.015**: 4.9 tiles across the 1.25 nook (0.255); 196 px sink door against 103 px tile (0.236 if the door is 450) | joints at the plinth lines, v6 t=73.10 and v6 t=100.73 | medium | ! (not in house.json) |
| 21 | street door | `d_street` 1.18 x 2.03 | - | half the opening is about three 200 mm pavers (0.6) | photo, rough | low | = |

Cross-check sums of the present spec (all close, by construction): X at the front 0.23 + 1.30 + 0.15 + 3.50 +
0.23 = 5.41; at the stairs 0.23 + 0.80 + 0.84 + 0.26 + 3.05 + 0.23 = 5.41; at the rear 0.23 + 1.10 + 0.15 + 2.50
+ 0.30 = 4.28 = 0.23 + 3.75 + 0.30. Y on the west side 0.12 + 1.73 + 0.10 + 3.22 + 2.63 + 1.05 + 0.30 + 3.20 +
0.13 + 4.50 + 0.50 = 17.48; on the east side 0.12 + 0.99 + 4.20 + 0.12 + 3.42 + 0.63 + 0.78 + 0.12 + 1.97 + 0.13 +
4.50 + 0.50 = 17.48. Proposal 6 keeps the sums by thickening `w_party_w_dining` (outer face unchanged).

## 3. Proposed spec changes

1. **Dining ceiling 2.80 -> 2.70** (`rooms.dining.ceilingZ`; heights of `w_party_w_dining`, `w_flank_dining`,
   `w_dining_n`, `w_dining_s_utility` 2.8 -> 2.7). The cornice's lower edge is at 2.55, not 2.65: this part
   is firm. The ceiling itself is that plus the cornice drop, which I could not measure (its top edge is not
   in the wall plane); 2.70 keeps the 0.15 profile of dining.md. Visible consequence: the crest plaques
   (about 0.22 high) nearly fill the band between the doorcase cap (2.22) and the cornice (2.55); in the
   model that band is 0.43. Knock-on: the north-wall pelmet (now 2.50-2.65) must end under 2.55; the floor
   zone to the first floor (3.04) becomes 0.34; nothing else moves.
2. **Dining west wall x -0.65 -> -0.59** (`rooms.dining.polygon`, `size` [3.69, 4.5]; `w_party_w_dining`
   thickness 0.23 -> 0.29, centreline x -0.735). The door does not move: on the hall side it is already
   0.045 from the pilaster face at x -0.59, so the dining wall is in the pilaster plane rather than the
   plane of the hall's main west wall. Neighbour that gives way: nobody (the party wall thickens inward).
   Items keyed to the dining west wall move +0.06 in x.

Withdrawn: from v2 t=790.50 alone the living-room wall strip north of the door read 0.10 (spec 0.24), which
would have moved the north wall 0.14 south. The second frame gives 0.21-0.25; the first is a grazing view in
which the architrave hides part of the strip. No change.

## 4. Notes per unit

**dining** — (a) ceiling and wall heights as proposal 1; cornice lower edge at Z 2.55; plaques band 2.22-2.55.
(b) West wall at x -0.59 (proposal 2): the dark doorcase stands tight in the SW corner, about 0.015 between
its west architrave and the west wall, and the west-wall dado rail and skirting start at the architrave
(v2 t=26.27, t=24.20). (c) Door leaf 0.838 x 1.981; dark architraves 0.085 wide; cap underside 2.08, top
2.22. (d) Dado rail top 1.047, 0.045 deep; skirting top 0.18. (e) 3-gang plate 0.146 x 0.086, centre
(0.64, 12.36, 1.35). (f) TV bottom edge 1.13, top 2.11, west edge x 0.89; if it is modelled 1.89 wide it is
probably too large (0.98 high suggests about 1.74 wide) — east edge not seen in my still. (g) Boards run
along Y, pitch 0.24.

**hall** — front hall 1.30 and corridor 1.10 stand; board pitch 0.24 along Y (five full boards and two cut
ones across the front hall: cut board 0.55 pitch at the west wall, 0.72 at the east wall; joints at 0.13,
0.38, 0.62, 0.86, 1.11 from the west skirting). Inner frame top 2.82. Corridor end-wall cornice lower edge
about 2.67.

**living** — NW chamfer position and size confirmed (wall strip 0.20 +/- 0.04 between the door architrave and
the chamfer, face 0.52-0.58, double socket on it, brass door stop near its north end). v10 (new footage) is
table-top only: xiangqi board with dark red disc pieces on the coffee table, inlaid mosaic domino box with a
red-lined hinged lid, round solitaire board with marbles on the bay table by the lamp base; no dimension
content. Boards run along Y (joints parallel to the TV wall in v2 t=831.93).

**kitchen** — floor tiles are about 0.245 wide, not 0.20 (five tile widths cross the 1.25 nook; white grout
lines 3-4 mm). Length not measured; the stagger is irregular. Room size not re-checked (section 5).

**shell** — if proposal 2 is taken: `w_party_w_dining` 0.29 thick; cornice, dado and skirting of the dining
room return on the new line. If proposal 1 is taken: the dining cornice sits 0.10 lower.

## 5. Not settled (keeps its present evidence)

1. **The whole Y chain of the hall** (front hall 3.22, passage 2.63, lobby 1.05, arch wall, corridor 3.20)
   and with it the living-room length 4.20: no better than the +/-0.25 of RECONCILE. A single near-field frame
   (v2 t=682.63) reads the stair bullnose 2.2-2.5 m from the inner doors against 3.22 in the spec, but the
   solution is not self-consistent (section 1) and I do not trust it. It is the largest possible error in the
   plan and needs either one tape measurement (inner doors to the newel) or a multi-frame reconstruction.
2. **Corridor width at the north end.** Spec 1.04 between pilaster and east wall; the board count gives
   1.08-1.16 and the end wall in v2 t=514.83 reads 1.43 x the door opening (1.20 +/- 0.08) against the
   verifier's 1.28 x in v1. Possibly 0.05-0.10 wider than modelled; not proposed.
3. **Dining width across** (3.69 by proposal 2, 3.75 now) and its length 4.50, chimney breast, side windows,
   French doors: not measured. The boards are too low in contrast to count across the room.
4. **Living width 3.50 and ceiling 2.95**: no frame has the door foot, door head and cornice together; the
   steep upward stills (v2 t=794.73) give 3.2-3.6 for the cornice, i.e. nothing. Bay, sill and head heights
   not measured.
5. **Kitchen 3.05 x 3.42, nook, back door, ceiling; utility; wc; vestibule** (width, depth, tile module,
   ceiling, street and inner door sizes): not re-measured. The kitchen tile pitch (0.245) makes a tile count
   of the kitchen possible in v6 t=73.10 / t=100.73 once the tile length is known.
6. **Passage width 0.80, arch, kitchen / utility / living / basement door widths and positions**: not
   re-measured.
7. Dining cornice drop (0.10-0.15) and therefore whether the ceiling is 2.66 or 2.71.

## Verification

Independent re-measurement of the two proposed `spec/house.json` changes (verifier; own stills and scripts in
`reference/work/r3_dims_G_v/` and `build/r3/dims_G_v/`, all private). I measured first and read sections 1-5
afterwards. Frames used are not the surveyor's: **v2 t=27.0** (door shut, 0.73 s after the surveyor's still, camera
moved), **v1 t=741 / t=740** (night video, door open, camera square to the south wall), **v1 t=719** (west wall).
Edges are sub-pixel gradient fits (rms 0.1-0.5 px), not hand picks.

| id | verdict | value to use | my measurement |
|---|---|---|---|
| dimsG-01 | **adjust** | `rooms.dining.ceilingZ` **2.62**; heights of `w_party_w_dining`, `w_flank_dining`, `w_dining_n`, `w_dining_s_utility` 2.62; `dining_chimney_breast.z` [0, 2.62]. Cornice **lower edge at Z 2.53**, which needs the `cornice_dining` profile (`blender/lib/mouldings.py`) cut from a 0.150 drop to **0.09** (projection 0.13 -> about 0.12). If the profile is left at 0.15 in this round, use 2.68 instead so that the lower edge still lands on 2.53 (the surveyor's 2.70 is then within tolerance). | Cornice lower edge: **2.51** (2.496-2.529 along the wall) by a wall-plane homography from the four fitted corners of the 0.838 x 1.981 leaf, v2 t=27.0; checks in the same solution: 3-gang plate 0.144 x 0.084-0.086, floor line 0.003, skirting 0.19, cap top 2.22; +/-1.5 px on the corners moves it 0.006. **2.54** by vertical cross-ratio on the east jamb, v1 t=741 (floor, lining head 1.995, vertical vanishing point from four verticals, y 6740 +/- 40 leave-one-out; 2.50-2.57 if the point is 25 % off). **2.52** at four columns of the west wall, v1 t=719, dado top 1.07 as scale. Mean 2.52-2.53, so the surveyor's 2.55 +/- 0.03 holds. The old 2.65 is the same picture read without the vanishing point (I get 2.67 that way). **Ceiling:** the ceiling line of the cornice, projected on the wall plane, lies only 0.134 (v1 t=741), 0.132-0.136 (v2 t=27.0) and 0.139-0.142 (v1 t=719) above the lower edge, from 1.5-2.2 m away. That figure is an upper bound of the drop (the ceiling line is nearer the camera and above it), so a 0.15 drop is excluded. Solving the south and west cornice runs together in v1 t=741 (rotation from the vertical and hall vanishing points, f 800-1100, principal point +/-60 px): projection 0.10-0.13, **drop 0.05-0.10, ceiling 2.58-2.64**. |
| dimsG-02 | **accept** | as proposed: dining west face **x -0.59**, size [3.69, 4.5]; `w_party_w_dining` thickness 0.29, centreline x -0.735 (outer face -0.88 unchanged); `d_dining` stays | Leaf west edge to the west wall, in the south-wall plane: west architrave outer edge **0.095-0.101**, visible corner **0.115** (plus up to 0.01 hidden behind the proud architrave) by the leaf homography, v2 t=27.0; east architrave 0.09 and cap overhangs 0.104 / 0.131 in the same solution. Second method, other video: in v1 t=741 the west wall face located from the lower edge of the west cornice run (3D, same calibration as above) is 0.93-0.98 from the east lining, i.e. **0.09-0.14, centre 0.115**, beyond the leaf edge; the opening itself comes out 0.79-0.80 for the expected 0.796, and the cap's west end is 0.00-0.03 from the wall. Present spec: 0.175, which would show 0.06-0.075 of plaster between architrave and corner; no frame shows it (v2 t=25, 27, 28; v1 t=740, 741). With the leaf edge at x -0.475 the wall is at **-0.59 +/- 0.02**. |

Knock-on checks.
- `python spec/validate_house.py <scratch copy> --no-draw` passes with both changes (and with either alone).
  X sum at the rear unchanged: 0.29 + 3.69 + 0.30 = 4.28. First-floor walls above (`w_party_w_1d`, face -0.65,
  breast to -0.55) stand on the thicker wall. Floor zone under the blue bedroom (3.04) becomes 0.42 (0.34 at 2.70):
  deep, plausible for a dropped ceiling with downlights; the riser chain is not touched.
- A foundation + dining preview from the scratch copy (`--house`, tag `r3dimsGv_c262w`) builds (BUILD OK) but shows
  what must follow in the same change, because `blender/rooms/dining*.py` hard-codes the old faces:
  `X0 = -0.65` buries the west-wall panels, mirror, plaques, dado run and the parked door stop in the thicker wall
  (all +0.06 in x); plaques at z 2.50, sword board 2.43, curtain track 2.49 and the pelmet 2.50-2.65 end up in the
  cornice. Measured in v2 t=27.0: south-wall plaques span **2.27-2.46** (centre 2.365, model 2.50); doorcase cap top
  2.22 (stays). The pelmet has to fit under 2.53; I did not measure it. The side-window cap (2.45) is about 0.1
  under the cornice edge in v1 t=634, which fits 2.53 and not the "0.20 below" of dining.md.
- Room centre moves +0.03 in x (ceiling rose, chandelier, downlight grid, table if they are keyed to the centre).

Not settled by me: the drop is 0.07 +/- 0.03, so the ceiling is 2.60 +/- 0.04; the three views are all from 1.5-2.2 m,
so projection and drop are separated only by the two-run solve of one frame. The v2 t=27.0 pose is too oblique to
repeat that solve (it returns 2.50-2.62 depending on the principal point). Dining width across, the rear-corridor
ceiling (2.84, deduced) and the hall-side position of `d_dining` were not re-measured; -0.59 rests on the door
staying where the hall evidence of RECONCILE V4 / V5 put it.
