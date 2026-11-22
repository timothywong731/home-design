# study (Rose Room) - round-3 brief

Module `blender/rooms/study.py` (id unchanged; the room's name is **Rose Room**). Decisions: `spec/RECONCILE3.md` (floor2b-01
.. -05, envelope-05, -06, garden-23).

## (a) What moved in the shell

- **Main room 0.31 deeper, neck 0.31 shorter**: the door wall stays (inner face y 13.04, `d_study` unchanged); the neck
  is 0.97 x 1.11 -> **0.97 x 0.80** (x -0.65..0.32), the main room's south wall moves from y 14.15 to **13.84**, so the main
  room is 3.75 x 2.71 -> **3.75 x 3.02** (y 13.84..16.86). The wall to bathroom2 (`w_bath2_study`) is now an ordinary 0.14
  partition (faces 13.70 / 13.84; the 0.45 unseen zone is gone). **South-wall furniture moves 0.31 south**; west-wall
  items keep their north-wall-tied positions; door-keyed items stay.
- Neck east wall on x 0.32 (partitions on centreline 0.37).
- **Window `w_study`**: 1.00 x 1.40, sill 0.68 -> **1.55 wide x 1.56 high, sill 0.58** (opening between the plaster
  reveals; head 2.14 above the floor), transom 1.75 -> **1.70**, centre x 1.26 -> **1.255** (the axis of the balcony and
  French doors). Four lights: **both lower lights top-hung**, opening out about 35 deg on friction stays, brass
  espagnolette centred on each bottom rail; both fanlights top-hung too. Interior reveal and oak board 0.24 deep
  (extReveal 0.24 -> 0.19 in the 0.50 wall).
- Flank wall 0.30 -> 0.35 thick outwards (inner face 3.10). Ceiling 2.60 unchanged (not re-measured here).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[study].polygon`: [[-0.65, 13.04], [0.3, 13.04], [0.3, 14.15], [3.1, 14.15], [3.1, 16.86], [-0.65, 16.86]] -> [[-0.65, 13.04], [0.32, 13.04], [0.32, 13.84], [3.1, 13.84], [3.1, 16.86], [-0.65, 16.86]]
- `rooms[study].size`: [3.75, 2.71] -> [3.75, 3.02]
- `walls[w_neck_bath2].a`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_neck_bath2].b`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_study_door].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_bath2_study].a`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_bath2_study].b`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_bath2_study].thickness`: 0.45 -> 0.14
- `walls[w_flank_2_study].a`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_flank_2_study].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_2_study].thickness`: 0.3 -> 0.35
- `walls[w_rear_2].b`: [3.25, 17.11] -> [3.275, 17.11]
- `openings[w_study].center`: [1.26, 17.11] -> [1.255, 17.11]
- `openings[w_study].width`: 1.0 -> 1.55
- `openings[w_study].height`: 1.4 -> 1.56
- `openings[w_study].sill`: 0.68 -> 0.58
- `openings[w_study].transomBar`: 1.75 -> 1.7
- `openings[w_study].sashes`: [{"light": "lower_w", "type": "side_hung", "hinge": "west", "swing": "out"}, {"light": "lower_e", "type": "side_hung", "hinge": "east", "swing": "out"}, {"light": "fanlights", "type": "top_hung", "swing": "out", "angle": 20}] -> [{"light": "lower_w", "type": "top_hung", "swing": "out", "angle": 35, "handle": "bottom"}, {"light": "lower_e", "type": "top_hung", "swing": "out", "angle": 35, "handle": "bottom"}, {"light": "fanlights", "type": "top_hung", "swing": "out", "angle": 20}]
- `openings[w_study].extReveal`: 0.24 -> 0.19
<!-- diff:end -->

## (b) Surveyors' notes (floor2_b, garden, dims_envelope merged)

As filmed 21 Nov (v13 f_0127-f_0206; stills in `reference/work/r3_floor2_b/`). z above the floor 6.02; y on the W wall tied
to the N wall face 16.86.

- Colours: W wall dusty rose, true about #C6ABA3 (model #BCA3A5 is fine); other walls soft white #F0EDE6; carpet pale
  neutral silver-grey #C6C4C0, lighter and less beige than carpet_pale; curtains #CECDC7 jacquard with large tone-on-tone
  leaf relief, pale-gold rope tie-backs with 0.2 tassel at z 0.95.
- Fixes: (1) wall TV is 55-inch, 1.23 x 0.71, y 14.83..16.06, z 1.23..1.94 (v4 f_0510, t193.4). (2) Radiator 7 oval
  tubes, 0.50 wide x 1.75-1.80 high, x -0.30..0.19, bottom at 0.21 (t148, v4 f_0444/f_0446). (3) A/C 0.80 x 0.30 x 0.22,
  x -0.62..0.18, z 2.10..2.40. (4) Rooster shadow box 0.34 x 0.58, y 16.25..16.59, z 1.25..1.83. (5) Cottage painting
  0.70 x 0.58, centre z 1.61, y 13.98..14.68; goose trophy centre y 14.49, z 2.23; antler plaque z 2.05..2.38 at y 15.42.
  (6) Three frames under the TV: black 0.17 sq at y 15.08..15.25, gold 0.30 x 0.34 at y 15.33..15.63 (top z 1.18), bronze
  0.18 sq at y 15.71..15.89; z 0.97..1.15. (7) Glazed bookcase y 15.00..16.02, 0.90 high (model 0.83). (8) Desk A (1.60 x
  0.80, rounded corners, black control strip under the front edge) 0.15-0.20 from the S wall - with the S wall now at
  13.84 its y is about 14.00..15.60 (the survey gave 14.32..15.92 against a 14.15 wall), x 1.55..2.35 (t170, t176). Desk B
  (1.20 x 0.70, castors) butting desk A's W edge, x 0.35..1.55 (v4 f_0444/f_0446, t128, t129) - keep its relation to desk
  A. (9) Add bean bag: lounger shape, dusty raspberry pink #B36A7C, NE corner, back to the E wall, x 2.20..3.05, y
  16.05..16.80, 0.55 high at the back (f_0151-f_0158, t166). (10) Plant pot at (1.00, 16.45). (11) E wall: add a double
  socket z 0.35 at y 15.25 below-north of the existing plate (z 1.05, y 14.95); S wall: double socket z 0.25 at x 2.35
  (t160, f_0178). (12) Dimmer 0.34 N of the door-wall face, cradle 0.12 further N (t127). (13) Six downlights as a 3 x 2
  grid: x 0.05 / 1.25 / 2.50, y 14.75 and 16.10; no proven neck light (v4 f_0566, f_0564, t193.4). (14) Curtain pole 1.88
  long, x 0.27..2.15 (centre it on the window axis 1.255), z 2.30. (15) Office chair: black fabric, winged ribbed back,
  red stitching - the current mesh is blocky. Certificate, whiteboard and all screens stay blank.
- Window from inside (t194.4, t206, t208): 1.55 two-light uPVC frame with transom; lock keeps on the bottom frame member;
  square white reveals 0.24 deep; oak board 0.24 deep + 25 mm rounded nose, full opening width. Measured opening 1.50-1.53
  between the plaster reveals, board 0.55-0.62, head 2.12-2.15, transom 1.64-1.78 (two surveys, v4 t443, t558.6). From
  outside the frame is 1.53 x 1.63, bottom Z 6.52, top 8.15, transom 7.67, stone sill 1.75 wide (v2 t248.5-t249.5). The
  real wall may be only 0.36-0.46 thick (exterior reveal about 0.08); kept at 0.50 with the error outside.
- Cornice: a small stepped ogee (fillet, cyma, bead, fillet), bottom edge 2.46, drop about 0.10, projection about 0.10 -
  not a plain 0.12 cove (t147, t193.4). Skirting 0.17 confirmed. Door: oak 4-panel leaf 686 hinged W, parks about 95 deg
  open with its free edge about 0.09 off the W wall, brass threshold strip.

## (c) New footage

- **v13** (PXL_20261121_132233957) **128-206** (the two office rooms: desks, monitors blank, bench, walls, TV, A/C, bean
  bag, plants) and **197-212** (window opened); 207-225 views down from this window onto the balcony, garden and shed.

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The south wall of the east part moved from y 14.15 to y 13.84; the notch is now x 0.32, y 13.04..13.84.
  - Now 0.31 off the wall: the art hangs in mid-air and the settee stands out in the room
    (`build/preview/study_settee_r3gate.jpg`).
    - `study.art.foliage` (x 1.79..2.31), `study.art.green_small` (x 1.90..2.10) and `study.art.octagon`
      (x 1.44..1.80), all at y 14.15..14.18
    - `study.settee` (x 0.38..1.43, y 14.163..14.674)
  - `study.ac_remote` (x 0.266..0.30, y 13.92..13.98, z 7.26..7.45) was on the notch face at x 0.30, which now ends at
    y 13.84, so it floats in the room.
- `w_study` widened from x 0.76..1.76 to x 0.48..2.03, and the bottom of the hole dropped from 6.70 to 6.60.
  `study.window_board` (x 0.45..2.06, z 6.701..6.726) now sits 0.10 above the new sill line, across the lower frame and
  glass. Lower it to the sill. Also check the curtain pole (x 0.328..2.192) and the drops against the wider window.
