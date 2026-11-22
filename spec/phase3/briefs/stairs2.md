# stairs2 (second flight + second-floor landing) - round-3 brief

Modules `blender/rooms/stairs2.py` (flight, balustrade, the virtual walls `v_head_jog`, `v_head_nosing`,
`v_platform_well`) and `landing2.py` (`landing2_head`, `landing2_platform`). Decisions: `spec/RECONCILE3.md` (floor2a-02,
-03, -04, -05; floor2b-01).

## (a) What moved in the shell

- **Hall east wall straight at x 0.32** from the stair-head corner (y 8.73) to the study door wall (y 12.94); was 0.22 to
  y 11.50 then 0.30. Hallway 0.87/0.95 -> **0.97** wide. Partitions `w_hall_purple`, `w_hall_bath2`, `w_neck_bath2`,
  `w_study_door` end on centreline x **0.37**. Everything hung on that wall moves east (switch S1 to (0.32, 9.10, z 1.20),
  harbour painting E1 centre y 9.75, double socket y 10.28, pier sockets y 12.56 / 12.78 at z 0.30, switch S3 y 12.68).
- **Stair head: interim jog.** `landing2_head` keeps the stair-head corner at x 0.15 and steps out 0.17 to 0.32 at y 8.73
  (`v_head_jog` (0.15..0.32, 8.73)). The footage shows **no jog**: the nosing line runs into the foot of the wall skirting
  (v13 t6, t5.5, t4.5; v4 t376, t379). Target for the stairs2 owner: platform east edge, balustrade, `v_head_nosing`
  and the stairwell well west edge at x **0.27**, polygon (-0.65,8.13) (0.27,8.13) (0.27,8.73) (0.32,8.73) (0.32,12.94)
  (-0.65,12.94). Until the flight is re-fitted the 0.17 jog is a known artefact.
- **Arch wall 0.30 north and thin**: `w_arch2` (and `w_purple_n`) 0.30 thick at y 11.35 -> **0.16 at y 11.58** (faces
  11.50..11.66). `a_landing2` width 0.87 -> **0.90**, centre (-0.20, 11.58), springing 1.74 -> **1.72**, crown 2.17:
  semicircle r 0.45, clear x -0.65..0.25, the west side dies into the party wall. New **east nib** x 0.25..0.32, y
  11.50..11.66, floor to springing (no spec field: build it in the module), its 0.16-wide west face carries a dado piece
  mitred and returned at both ends and a skirting block; the d_purple and d_bath2 architraves stand on the wall plane
  either side, 0.07 behind it. The second-floor arch wall no longer stands on the first-floor one (that is at 11.36..11.48).
- **Doors**: `d_purple` centre y 10.795 -> **11.095** (hinge 11.40); `d_bath2` 0.762 -> **0.686** leaf, centre y 11.951 ->
  **12.055**, clear y 11.71..12.40, hinge south (11.71). The pier north of d_bath2 is 0.54 to the end wall (12.94).
- Study door wall unchanged (inner face 13.04); landing2_head north edge 12.94 unchanged.
- The stair_second flight itself is unchanged (13 risers; going 0.23 now differs from the main flight's 0.253 - do not
  move its foot, y 6.06, until that is settled).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[landing2_head].polygon`: [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.22, 8.73], [0.22, 11.5], [0.3, 11.5], [0.3, 12.94], [-0.65, 12.94]] -> [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.32, 8.73], [0.32, 12.94], [-0.65, 12.94]]
- `rooms[landing2_head].size`: [0.87, 4.81] -> [0.97, 4.81]
- `walls[w_hall_purple].a`: [0.27, 9.01] -> [0.37, 9.2]
- `walls[w_hall_purple].b`: [0.27, 11.35] -> [0.37, 11.58]
- `walls[w_arch2].a`: [-0.765, 11.35] -> [-0.765, 11.58]
- `walls[w_arch2].b`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_arch2].thickness`: 0.3 -> 0.16
- `walls[w_hall_bath2].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_hall_bath2].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_study_door].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[v_head_jog].b`: [0.22, 8.73] -> [0.32, 8.73]
- `openings[d_purple].center`: [0.27, 10.795] -> [0.37, 11.095]
- `openings[d_purple].hingeAt`: [0.27, 11.1] -> [0.37, 11.4]
- `openings[d_bath2].center`: [0.35, 11.951] -> [0.37, 12.055]
- `openings[d_bath2].width`: 0.762 -> 0.686
- `openings[d_bath2].hingeAt`: [0.35, 11.57] -> [0.37, 11.71]
- `openings[a_landing2].center`: [-0.215, 11.35] -> [-0.2, 11.58]
- `openings[a_landing2].width`: 0.87 -> 0.9
- `openings[a_landing2].springing`: 1.74 -> 1.72
- `features[landing2_arch].springing`: 1.74 -> 1.72
- `features[landing2_arch].thickness`: 0.3 -> 0.16
<!-- diff:end -->

## (b) Surveyors' notes (floor2_a, floor2_b, dims_vert, dims_1 merged)

- Cat drawings: N1 (sitting black-and-white cat) on the stairwell north wall (y 8.73, x about 0.55, centre about 1.45
  above the floor); N2 (lying tabby) on the stairwell **east** wall (x 0.99, y about 8.35), about 0.35 lower, not on the
  north wall; both 0.45 x 0.35, narrow brushed-gold frame, white mount with a dark red-brown line; dado level on the north
  wall, raking down the east wall from the corner (v13 f5-f6).
- Wall below the dado is darker and warmer than modelled: luminance 0.45-0.55 of the white above (model 0.64); estimate
  #C0B9AD (present #C8C5BB) - same paint as the ground-floor hall, change both or neither.
- Confirmed: W1-W4, E1, two ceiling discs, platform step with the dado / skirting kink, skylight, newel #37211E, carpet,
  brass thresholds; trim: hall cove about 0.10, dado top 0.98-0.99, skirting 0.17, ceiling 2.60. Omit the white plug-in
  in the east-wall socket.
- Socket plate(s) on the hall east wall below the dado just south of the study door architrave (v13 t127).
- Second-floor platform (v13 t48): turning newel cap about 1.05 above the platform (model 1.20), handrail about
  0.95-1.0; the dado steps up with a short ramp beside the single riser; ceiling line 0.15 above the loft door lining head
  (2.14 +/- 0.02 above the loft threshold). The loft door is a 686 leaf (v4 t360, aspect 0.66-0.69), so the platform is
  about 0.90 wide, not 0.80. Loft door step 0.24 +/- 0.03 (v13 t48) against 0.27: inside tolerance, floor stays 6.49.
- Flight: 13 risers confirmed - ten square (R1..R10), two diagonal from the turning newel (R11, R12), one on the landing
  edge; at the newel the first diagonal riser sits directly above the tenth square riser (v4 t170.5, t175, t191; v6 t7).
- The well over the quarter landing has the landing's footprint (0.84 x 0.60); the landing may really be 1.04 deep (not
  adopted, see stairs.md).
- Frames: v13 f12-f17 (arch, t16 frontal), v4 t383-384 (arch, hall width), v13 t5-t6 (stair head from above).

## (c) New footage

- **v13** (PXL_20261121_132233957) **1-10**: hallway, dado, arch, balustrade; 11-17 the arch and the two doors; t48 the
  platform and loft door.

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The east face of `landing2_head` moved from x 0.22 to x 0.32 (y 8.73..12.94; the old 0.30 step at y 11.5 is gone).
  - 0.10 off the wall: `landing2_head.picture.harbour` (x 0.19..0.22, y 9.26..10.24, z 7.28..7.96),
    `landing2_head.socket.0` (x 0.206..0.22, y 10.207..10.353) and `landing2_head.switch.s1` (x 0.205..0.22,
    y 9.057..9.143).
  - 0.02 off the wall: `landing2_head.socket.1`, `.socket.2` and `.switch.s3` (x 0.285..0.30, y 12.49..12.84).

  Move them to x 0.32. `d_purple` is now at y 10.79..11.40, clear of the harbour picture.
- `stairs2.wall_string` touches `landing2_head.skirting` at (0.30, 9.72, 6.14). Only 2 triangles; cosmetic.
- The flight itself (spindles, strings, handrail, carpet) shows nothing broken.
