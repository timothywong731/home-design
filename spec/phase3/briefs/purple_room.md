# purple_room (Lavender Room) - round-3 brief

Module `blender/rooms/purple_room.py` (id unchanged; the room's name is **Lavender Room**). Decisions: `spec/RECONCILE3.md`
(floor2a-02, -04, -06, -07; envelope-03).

## (a) What moved in the shell

- **Room moved north and is 0.10 narrower**: x 0.32..3.10 x y 9.29..11.20 (2.78 x 1.91) -> **x 0.42..3.10 x y 9.55..11.50
  (2.68 x 1.95)**. The west (hall) wall moved 0.10 east (centreline 0.37); the north wall (`w_purple_n`, shared with the
  arch wall) is 0.16 thick on centreline 11.58 (faces 11.50 / 11.66); the south wall (`w_addition_s_2`, the old rear wall
  of the main house plus an unseen zone) is 0.70 thick on 9.20 (faces 8.85 / 9.55). **Re-fit everything from the north
  wall**: positions keyed to the north wall keep their offsets from it.
- **Door `d_purple`** centre y 10.795 -> **11.095**, hinge y 11.40 (the door stays 0.10 from the north wall).
- **Window `w_purple`**: width 0.75 -> **0.82**, centre y 10.25 -> **10.47** (1.03 from the north wall, over the
  first-floor window axis 10.475), transom bar 1.60 -> **1.50**; sill 0.76 and height 1.42 kept. Lower light **top-hung**,
  opening out about 30 deg on friction stays, brass espagnolette centred on the bottom rail; upper light fixed with a
  white trickle vent. Flank wall 0.30 -> 0.35 thick outwards (inner face 3.10), extReveal 0.07.
- Floor 6.02, ceiling 2.60 unchanged (not re-measured in this room).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[purple_room].polygon`: [[0.32, 9.29], [3.1, 9.29], [3.1, 11.2], [0.32, 11.2]] -> [[0.42, 9.55], [3.1, 9.55], [3.1, 11.5], [0.42, 11.5]]
- `rooms[purple_room].size`: [2.78, 1.91] -> [2.68, 1.95]
- `walls[w_addition_s_2].a`: [0.27, 9.01] -> [0.37, 9.2]
- `walls[w_addition_s_2].b`: [3.25, 9.01] -> [3.275, 9.2]
- `walls[w_addition_s_2].thickness`: 0.56 -> 0.7
- `walls[w_hall_purple].a`: [0.27, 9.01] -> [0.37, 9.2]
- `walls[w_hall_purple].b`: [0.27, 11.35] -> [0.37, 11.58]
- `walls[w_purple_n].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_purple_n].b`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_purple_n].thickness`: 0.3 -> 0.16
- `walls[w_flank_2_purple].a`: [3.25, 9.01] -> [3.275, 9.2]
- `walls[w_flank_2_purple].b`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_flank_2_purple].thickness`: 0.3 -> 0.35
- `openings[d_purple].center`: [0.27, 10.795] -> [0.37, 11.095]
- `openings[d_purple].hingeAt`: [0.27, 11.1] -> [0.37, 11.4]
- `openings[w_purple].center`: [3.25, 10.25] -> [3.275, 10.47]
- `openings[w_purple].width`: 0.75 -> 0.82
- `openings[w_purple].transomBar`: 1.6 -> 1.5
- `openings[w_purple].sashes`: [{"light": "lower", "type": "side_hung", "hinge": "south", "swing": "out", "angle": 80, "handle": "bottom"}, {"light": "upper", "type": "fixed"}] -> [{"light": "lower", "type": "top_hung", "swing": "out", "angle": 30, "handle": "bottom"}, {"light": "upper", "type": "fixed"}]
- `openings[w_purple].extReveal`: 0.02 -> 0.07
<!-- diff:end -->

## (b) Surveyors' notes (floor2_a, dims_vert merged)

Frames v13 f19-f27, f39-f40; v4 t389, t390.5. Positions below were given in the survey's frame (room y 9.29..11.20, i.e.
before the move): **add +0.30 to every y** to place them in the new room (they keep their offset from the north wall).

- Wall colour: samples #B5B4C4 reveal, #BCBFC4 / #BFBCC4 west wall, #AAA9C4 north wall; normalised to the skirting
  (#B8B7C8 at luminance 0.54 of white); estimate under neutral light #B9B5C6 (present #B4AFC6 is close; slightly
  lighter, less saturated).
- Oak window board about 0.85 x 0.27 x 0.03, rounded nose (true about #B58A5E). Frame 0.85-0.90 outside the 0.82 reveal.
- Radiator: white sectional, **seven wide round-topped sections** at about 73 mm pitch, 0.52 wide x 0.45 high x 0.10
  deep, y 9.93..10.45 (survey frame), z 0.17..0.62 (bottom level with the skirting top, 0.09 under the board), valves low at
  the south end - replaces the 9 thin columns 0.60 high (v13 f20-f24).
- Curtains: eyelet heading wrapping the pole, off-white ground, dusty-rose peony heads 0.20-0.25 across (two to three per
  curtain width, about twice the model's motif), long sage / grey-green leaves, gold rope tie-backs with tassels at z
  0.88, hem 0.30 above the floor. Pole mid-brown wood about #8B5E3C (not near-black), dia 30-35, ball finials, about 1.58
  tip to tip, y 9.40..10.98 (survey frame), z 2.33, 0.09 off the wall.
- A/C unit on the south wall moves west to clear the finial: x 2.05..2.85, z 2.18..2.47 (0.25 from the east wall).
- West wall (x 0.42): remote cradle y about 10.22 and one-gang dimmer y about 10.33 at z 1.25-1.35; double socket centre
  y 10.03, z 0.33 (+/- 0.08) (survey frame).
- North-wall socket, south-wall twin plate, four downlights, carpet (about #BDB9B2) as present; room unfurnished, the
  Chippendale chair may stay.
- The window looks across the side passage at a brick wall with clearly resolved courses (v13 f_0022-0038): counting them
  from the passage paving to the window level would give an independent height for the second floor (not done).

## (c) New footage

- **v13** (PXL_20261121_132233957) **11-49**: door, floral curtains, radiator, window opened, view down onto the side
  passage.

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

The room moved. Its polygon was x 0.32..3.10, y 9.29..11.20 and is now x 0.42..3.10, y 9.55..11.50: the south wall moved
0.26 north, the west wall 0.10 east and the north wall 0.30 north. `w_purple` is now y 10.06..10.88 and 0.82 wide (it was
y 9.875..10.625). `d_purple` is now at x 0.37, y 10.79..11.40. Re-lay the room from the new polygon and openings, with no
literal coordinates. See `build/preview/purple_room_south_r3gate.jpg`.
- Buried in the south wall (y 9.55):
  - `purple_room.aircon` and `purple_room.aircon.louvre` (x 2.25..3.05, y 9.29..9.50, z 8.20..8.49): entirely inside it
  - `purple_room.outlet_plate` (x 1.527..1.613, y 9.29..9.30): inside it
  - `purple_room.chair` (x 1.569..2.171, y 9.311..9.885): its back is 0.24 inside it
  - `purple_room.ceiling_disc` (x 1.71..1.83, y 9.53..9.65): straddles it
- Buried in the west wall (x 0.42), poking through into `landing2_head`: `purple_room.aircon.remote` (x 0.32..0.345,
  y 10.205..10.275), `purple_room.dimmer` (x 0.32..0.343, y 10.287..10.373) and `purple_room.socket.0` (x 0.32..0.334,
  y 9.767..9.913).
- At the window:
  - `purple_room.window_board` (x 3.07..3.321, y 9.85..10.65): its south 0.21 runs into the reveal side and its north
    end stops 0.23 short.
  - `purple_room.trickle_vent` (y 10.05..10.45, z 8.16..8.19) is still on the old window head and crosses the new reveal.
- Standing off: `purple_room.socket.1` (x 2.597..2.743, y 11.186..11.20) is 0.30 off the moved north wall.
- Off-centre against the moved window: `purple_room.radiator` (y 9.952..10.50) and the curtain set (pole y
  9.528..10.972, hooks y 9.867..10.633, drops y 9.57..10.93).
- Repaint: the walls are '#B9B5C6' (shell request).
