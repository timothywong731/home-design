# living - round-3 brief

Module `blender/rooms/living.py`. Decisions: `spec/RECONCILE3.md` (front-04, porch-06/-07, envelope-01/-02, front-12).

## (a) What moved in the shell

- **Bay shifted 0.07 west**: the four lights are centred on x **2.48** (was 2.55; lights x 1.175..3.785). The square bay
  keeps 2.90 x 0.99 inside: x 1.10..4.00 -> **1.03..3.93**. Nibs are now **0.23 west / 0.37 east** (were 0.30 / 0.30).
  Nib chamfers move to the corners (1.03, 0.99) and (3.93, 0.99).
- **West cheek wall** `w_bay_cheek_w`: 0.20 -> **0.28** thick, faces x 0.75 (vestibule) / 1.03 (bay). The return light
  `w_bay_cheek_w` moved to y **0.63** (glass y 0.405..0.855), width 0.45; its frame is near the vestibule face, so the
  living side has a deep reveal - new feature `living_bay_cheek_w_reveal` (0.20 deep, x 0.83..1.03, z 0.62..2.70) with the
  shutter inside it. Depth not measured from the living room.
- **East cheek wall** `w_bay_cheek_e`: 0.15 -> **0.32** thick, faces 3.93 / 4.25 (outer face 0.40 behind the east wall
  face). Return light `w_bay_cheek_e` y 0.37 -> **0.43** (frame y 0.17..0.69).
- **East wall** (`w_party_e_living`, an external wall facing the alley, id kept): 0.23 -> 0.35 thick outwards; inner face
  x 4.30 unchanged.
- Room size 3.50 x 4.20, ceiling 2.95 unchanged.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[living].polygon`: [[0.8, 0.99], [1.1, 0.99], [1.1, 0], [4.0, 0], [4.0, 0.99], [4.3, 0.99], [4.3, 5.19], [1.21, 5.19], [0.8, 4.78]] -> [[0.8, 0.99], [1.03, 0.99], [1.03, 0], [3.93, 0], [3.93, 0.99], [4.3, 0.99], [4.3, 5.19], [1.21, 5.19], [0.8, 4.78]]
- `walls[w_front_bay].a`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_front_bay].b`: [4.075, -0.06] -> [4.09, -0.06]
- `walls[w_bay_cheek_w].a`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_bay_cheek_w].b`: [1.0, 0.865] -> [0.89, 0.865]
- `walls[w_bay_cheek_w].thickness`: 0.2 -> 0.28
- `walls[w_bay_cheek_e].a`: [4.075, -0.06] -> [4.09, -0.06]
- `walls[w_bay_cheek_e].b`: [4.075, 0.865] -> [4.09, 0.865]
- `walls[w_bay_cheek_e].thickness`: 0.15 -> 0.32
- `walls[w_front_nib_w].b`: [1.1, 0.865] -> [1.03, 0.865]
- `walls[w_front_nib_e].a`: [4.0, 0.865] -> [4.09, 0.865]
- `walls[w_front_nib_e].b`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_vest_living].b`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_hall_living].a`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_cross].b`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_living].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_party_e_living].b`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_living].thickness`: 0.23 -> 0.35
- `openings[w_bay_front].center`: [2.55, -0.06] -> [2.48, -0.06]
- `openings[w_bay_cheek_w].center`: [1.0, 0.37] -> [0.89, 0.63]
- `openings[w_bay_cheek_w].width`: 0.5 -> 0.45
- `openings[w_bay_cheek_e].center`: [4.075, 0.37] -> [4.09, 0.43]
- `features[living_bay].polygon`: [[1.1, 0.0], [4.0, 0.0], [4.0, 0.99], [1.1, 0.99]] -> [[1.03, 0.0], [3.93, 0.0], [3.93, 0.99], [1.03, 0.99]]
- `features[living_bay].chamfers`: [{"corner": [1.1, 0.99], "width": 0.15, "z": [0, 2.2], "stop": [2.2, 2.4]}, {"corner": [4.0, 0.99], "width": 0.15, "z": [0, 2.2], "stop": [2.2, 2.4]}] -> [{"corner": [1.03, 0.99], "width": 0.15, "z": [0, 2.2], "stop": [2.2, 2.4]}, {"corner": [3.93, 0.99], "width": 0.15, "z": [0, 2.2], "stop": [2.2, 2.4]}]
- `features[living_bay_cheek_w_reveal]` new: {"id": "living_bay_cheek_w_reveal", "level": "G", "type": "reveal", "room": "living", "polygon": [[0.83, 0.405], [1.03, 0.405], [1.03, 0.855], [0.83, 0.855]], "z": [0.62, 2.7]}
<!-- diff:end -->

## (b) Surveyors' notes (living_games, front, porch, dims_G, dims_envelope merged)

**Table games, owner instruction** (v10 throughout; stills tSS_fNNNN / gNNNN in `reference/work/r3_living_games/`; full
per-piece table in `spec/phase3/living_games.md` section 2.1). World frame; coffee table centre (2.80, 2.33), top z 0.46,
east edge x 3.11, south end y 1.53; lamp table centre (2.55, 0.37), top z 0.64.

1. **Xiangqi set** - remove from the TV unit, rebuild on the coffee table (v10 f_0001-0008; t03_f0105, t00_f0021). Board
   slab 0.43 (N-S, across files) x 0.475 (E-W, along files) x 0.015, eased edges, no feet; walnut oiled satin (estimate
   #6B4F3C, cells alternating #7E6350 / #5C4436), flush maple strips 4.5 mm (#D9C7A6), margin 38 mm. 9 file x 10 rank
   lines, cell 44.5 mm (grid 356 x 400.5); outer files full length, the 7 inner ones stop at the river (one clear cell);
   palace X over the middle three files and first three ranks at each end; no corner marks, no lettering - one generated
   texture. 32 discs dia 38 x 15, arrises 2.5 mm, all dark maroon (#4A2428 satin); incised glyph on the top face only, 3-5
   strokes about 20 mm high: 16 rose-red (#C8505C) on the east army upright seen from the east, 16 turquoise (#4FB3A6) on
   the west army upright seen from the west. Standard opening array, casually placed (per-piece centres +/-0.07 cell in
   the notes); red back rank bowed up to 0.75 cell towards the river in the middle, its chariots half a cell in from the
   corners. Placement: centre (2.845, 2.15), bottom z 0.46, red edge on the table's east edge, twisted 5 deg with the south
   end further east; rot_z -85 deg with local +x = files north to south, +y towards red; piece (u, v): local x =
   (u-4)*0.0445, y = (4.5-v)*0.0445.
2. **Inlaid domino box** - remove from the lamp table, rebuild on the coffee table (f_0009-0043; t40_f1219, t38_f1159,
   t32_f0964, t33_f1006, g1183, g0604). 0.145 x 0.097 x 0.042 (lid 12 mm, base 30), lid its own object with an ix
   open/close, hinged on a long side, stands open at about 100 deg. Red-brown hardwood carcass (#5E3A2C), underside with a
   6 mm bone border. Lid: 11 mm border of fine black/white pinstripes with bone corner squares; 1 mm white / 2 mm red-brown
   (#7A4A3C) / 1 mm white; field 0.117 x 0.066 on black (#24272B) with a star-and-hexagon lattice in 3 mm dotted bands,
   five mother-of-pearl six-pointed stars 19 mm in a quincunx (+/-30 mm along, +/-22 mm across; half stars cut by the frame
   on the short sides) and 12 hexagon rosettes 14 mm (three rows of four). Bone #EDE9DF, mother-of-pearl #EFF0F5 glossy.
   Sides: inset two-row lozenge chevron panels (long 0.118 x 0.020, short 0.070 x 0.020), 6 mm striped corner posts, three
   white stringing lines on the lid edge. Crimson velvet lining (#A01C24). 28 cream dominoes 48 x 24 x 7.5 (#EEEADB),
   black pips, brass centre pin, four layers of seven. Loose tiles (at most three, only with the lid open, or none): box
   frame (+0.03, 0.085) parallel, (+0.10, 0.035) at 55 deg, (+0.17, 0.02) at 10 deg. Placement: centre (2.85, 1.70), z 0.46,
   long axis NE-SW, hinge side faces SE, rot_z -131 deg (+/-10). Lid pattern generated from this description (a
   rectified crop is possible only if the orchestrator rules marquetry an art pattern: t40_f1219 quad (480,782)
   (930,1090) (735,1425) (255,1080)).
3. **Solitaire** stays on the lamp table (f_0045-0065; t56_f1690, t60_f1816, t64_f1942, g1369): turned burr-wood board
   dia 0.24 x 15 mm, high polish, flat field dia 0.188 ending in a 1.5 mm bead, concave groove 13 mm wide x 4 deep, rounded
   lip 12 mm; #7A5238 with swirls #4A3226 and golden patches #A07850. English cross, 33 holes at 23.8 mm pitch, **all 33
   filled** with 20.5 mm onyx marbles (cream #E6E1D3, honey/tan #CDBF9C / #A8906A, banded brown/cream #8E7359, random) -
   the model has 32 of 17 mm at 25 mm. Placement (2.57, 0.415), z 0.64, lattice turned about 9 deg.
4. **Lamp base** (t46_f1385, t56, t64, g1369): bottom to top - pierced gilt acanthus ring foot dia 0.18 on the table;
   domed rose-brown mottled marble foot dia 0.145, 35 high; torus neck ring 50 mm at about 0.06; plain inverted-cone marble
   body widening from 45 mm to about 0.13 at a gilt rose-garland collar about 0.25 above the ring. Marble #B5846B, gilt
   #A8914F. Centre (2.62, 0.245); gold flex towards the window. Body top and shade not in v10: keep.
5. **Curtains**: hem 0.27 +/- 0.04 above the floor (about 0.10 above the skirting top; t42_f1273, f_0010, v2 f_0873); the
   model has 0.12 in both states. Red bands in daylight raspberry-wine #9A4A55.
6. **Rug**: bare floor shows between coffee table and sofa, so the east edge is x <= 3.35 (model 3.50) and the west edge
   about 2.0 +/- 0.1: shift 0.10-0.15 west (centre x about 2.68). Better daylight crops: t00_f0021, g1309.
7. **Armchairs**: two-tier arms - thick roll pad on a flat upholstered pad with gimp at its lower edge, on the dark arm
   rail, front post with a ball finial (g1309, t42). East chair has no loose cushion in v10.
8. Footstool in v10 at about (2.5, 1.05) in front of the lamp table (movable, low priority).
9. **Brass magazine rack** on the floor between the east nib and the east armchair, about (3.80, 0.85): embossed sheet
   brass 0.30 x 0.15 x 0.26 high, splayed sides, empty (t42, f_0009-0012, f_0038); replaces the optional cake-stand.
10. Coffee table size, moulding and the 0.52 gap to the sofa are right; top is dark stained oak (#4B3D35-#695A4D), less
    regular lower-contrast grain, glossier.
11. Velvet daylight samples are redder (sofa #A35451, armchair #A65F5D) than the nap map (#8B5631): estimate #A2584A,
    low-medium confidence.
Declutter: grey throw, remotes, the white plastic box in the bay and the stain on the lamp table are omitted.

**Bay**: from outside the lights are 4 x 0.54 with 0.15 mullions, each of the 8 openings with a raised moulded
architrave about 0.04 wide; lights 1 and 4 of both rows are opening sashes with a second frame, 2 and 3 fixed; outer
frames white. About 0.2 m is unaccounted for between light 4 and the east wall (the lights may be 0.57-0.58 wide, or
stand further east): a shutter-panel or sill-board measurement inside would settle it. Shutters (lib/joinery._shutter
63 mm louvres at about 52 mm pitch): v10 shows 11 blades over 0.68-0.83 of the east return panel and blade pitch /
stile width 1.35-1.5, i.e. pitch 70 +/- 8 mm (76 or 89 mm blades, 13-15 per lower panel); low-medium confidence, change
only if the v9 views agree (v9 59-68). NW chamfer confirmed: flat strip 0.20 +/- 0.04 between the door's north architrave
and the chamfer, chamfer face 0.52-0.58 with the double socket on it and the brass door stop near its north end (v2
t718.4, t790.5). Boards along Y, pitch 0.24. Width 3.50, length 4.20, ceiling 2.95 and window heights were not
re-measured.

## (c) New footage

- **v10** (PXL_20261121_124801398) whole video: table games close up, rug, sofa and armchairs behind.
- v9 59-68: forecourt along the bay base, shutters seen through the glass; v8 13-66 the bay from the street.

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

The bay dressing is still placed for the old bay (x 1.10..4.00). The bay is now x 1.03..3.93, 0.07 further west.
- `living.curtain_track` runs x 1.165..3.935; it should run about 1.095..3.865. Its east end crosses
  `living.w_bay_cheek_e.timber` (x 3.92..4.04) and the cornice.
- `living.curtain.2`, `living.curtain.3` and `living.curtain.closed` cross `living.bay.sill`, `living.skirting` and the
  east cheek timber.
- `living.curtain.3.tieback` (x 3.784..3.988, y 0.659..0.88) is 0.06 inside the east nib. `living.curtain.2.tieback`
  (x 3.712..3.933) cuts the cheek timber.
- The west side now stands off the wall. `living.curtain.0` (x 1.187..1.277, y 0.392..0.872) and
  `living.curtain.0.tieback` (x 1.112..1.316) are 0.07 further from the west bay face (x 1.03) than before;
  `living.curtain.1` and its tieback likewise.
- Shift the whole bay set 0.07 west, then check the side drops against the moved return lights (west y 0.405..0.855,
  behind a 0.20 reveal; east y 0.18..0.68).
- The armchairs, lamp table and table lamp in the bay are clear of the new walls.
