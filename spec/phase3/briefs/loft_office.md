# loft_office (Slate Room) - round-3 brief

Module `blender/rooms/loft_office.py` (id unchanged; the room's name is **Slate Room**). Decisions: `spec/RECONCILE3.md`
(eaves_loft-01..-05, -08, -09; floor2b-06; front-06).

## (a) What moved in the shell

- **Front knee wall 0.92 -> 1.08** high (y 2.54 unchanged). The front ceiling plane is a **stopgap** that keeps the
  envelope as it is: `front_slope` z = 6.30 + 0.50 y (26.6 deg; was 5.9435 + 0.57735 y, 30 deg), from 1.08 at the knee
  wall (Z 7.57) to the flat 2.12 at y 4.62. The gable walls read 35 deg on both sides: the front half of the section is an
  **open question** (see RECONCILE3), and the stopgap leaves only about 0.15 between ceiling and roof top at the knee wall
  (the envelope test flags the 0.30 roof slab there).
- **Rear slope 30 -> 35 deg**, turned about the unchanged ridge: `rear_slope` z = 12.33 - 0.70 y, from the flat at y 5.31
  (was 5.38) down to the rear knee wall; **rear knee wall 1.42 -> 1.23** (y 6.59 unchanged). The flat strip is y 4.62..5.31
  east of x 1.25 (0.69 wide), 4.62..5.38 west of it; apex 2.12 unchanged. Lobby (x -0.65..0.31, y 5.38..6.13, flat 2.08)
  unchanged.
- **Hatches**: front pair `h_eaves_front_w` / `_e` 0.70 high sill 0.15 -> **0.90 high, sill 0.03** (width 1.05); the east
  one moves from x 2.975 to **2.48**, on the axis of the bay-gable tunnel (= the gable ridge); the west one stays at
  0.175. Rear pair `h_eaves_rear` 1.03 / 0.17 -> **0.91 / 0.15** under the 1.23 knee wall.
- **Velux** z 7.99..8.55 -> **7.82..8.49** (on the 35-deg plane).
- East wall 0.23 -> 0.35 thick outwards (inner face 4.30). Floor 6.49 unchanged.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[loft_office].ceiling.planes[front_slope].z.c0`: 5.9435 -> 6.3
- `rooms[loft_office].ceiling.planes[front_slope].z.cy`: 0.57735 -> 0.5
- `rooms[loft_office].ceiling.planes[flat].polygon`: [[-0.65, 4.62], [4.3, 4.62], [4.3, 5.38], [-0.65, 5.38]] -> [[-0.65, 4.62], [4.3, 4.62], [4.3, 5.31], [1.25, 5.31], [1.25, 5.38], [-0.65, 5.38]]
- `rooms[loft_office].ceiling.planes[rear_slope].polygon`: [[1.25, 5.38], [4.3, 5.38], [4.3, 6.59], [1.25, 6.59]] -> [[1.25, 5.31], [4.3, 5.31], [4.3, 6.59], [1.25, 6.59]]
- `rooms[loft_office].ceiling.planes[rear_slope].z.c0`: 11.7147 -> 12.33
- `rooms[loft_office].ceiling.planes[rear_slope].z.cy`: -0.57735 -> -0.7
- `walls[w_east_2b].a`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_east_2b].b`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_east_2b].thickness`: 0.23 -> 0.35
- `walls[w_knee_front].b`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_knee_front].height`: 0.92 -> 1.08
- `walls[w_knee_rear].b`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_knee_rear].height`: 1.42 -> 1.23
- `openings[h_eaves_front_w].height`: 0.7 -> 0.9
- `openings[h_eaves_front_w].sill`: 0.15 -> 0.03
- `openings[h_eaves_front_e].center`: [2.975, 2.49] -> [2.48, 2.49]
- `openings[h_eaves_front_e].height`: 0.7 -> 0.9
- `openings[h_eaves_front_e].sill`: 0.15 -> 0.03
- `openings[h_eaves_rear].height`: 1.03 -> 0.91
- `openings[h_eaves_rear].sill`: 0.17 -> 0.15
- `features[velux].z`: [7.99, 8.55] -> [7.82, 8.49]
<!-- diff:end -->

## (b) Surveyors' notes (eaves_loft, floor2_b, dims_vert merged)

- **Hatches** (all three are pairs hinged on the outer stiles, opening into the room 95-100 deg; v12 f1, f7-14, f44-48,
  f64-68, f73-80, f118-122; v5 t245-248): flat white 18 mm lay-on leaves, front 0.46-0.48 x 0.80-0.82 at z 0.07-0.89 above
  the carpet, rear 0.46-0.48 x 0.84-0.88 at z 0.18-1.02; two concealed nickel cup hinges per leaf about 0.10 from top and
  bottom; polished-brass mushroom knob about 30 mm, 0.165 below the leaf top and 0.095 from the meeting edge (z 0.72 front,
  0.93 rear) - not at mid height. Round each pair a white ogee architrave about 45 mm, mitred, 20 mm proud (outer 1.04
  wide; front z 0.03-0.93, rear 0.15-1.06); outside that a thin applied panel bead about 20 mm forming a rectangle 80 mm
  outside the leaf edges at the sides and 75 mm above the leaf top (1.11 wide, top at z 0.96 front / about 1.10 rear),
  uprights down to the skirting. No other panels, no dado rail, no capping rail; the slope starts at a plain arris. Front
  hatches have one 65 mm moulded member between carpet and leaf bottom; the rear hatch has a bottom architrave on a 0.10
  skirting.
- Skirting about 0.09 high with a small moulded top (spec 0.15; f43, f69).
- Bookcase x 0.82..1.72 is 1.06 high with its top at the slope line, framed-panel ends and a thick top with rounded front
  corners (f4-6, f64); a shredder fills the gap between the east hatch's architrave and the bookcase (v12 t0.2) - with the
  hatch at 2.48 the frame spans x 1.96..3.00.
- Ensign at the SW corner of the west wall: 0.61 x 0.91 flag hung vertically from the slope line, y 2.60..3.21, z
  0.10..1.02 (with the stopgap slope it may need to come down to stay under the ceiling).
- Colours: carpet neutral silver grey in daylight (estimate #B6B3AC); slopes a shade greyer (#C9CBCA sampled) than knee
  walls and joinery (estimate #F2F2EF); east gable dark blue-grey (sampled #474D53 / #34383B, true about #3B4046),
  unchanged - no pink anywhere.
- Radiator 20 oval columns about 1.27 x 0.57, no change. Model inventory matches v5 f_0166-f_0262 and v12 (unchanged).
  Raise detail on: mesh office chair (white shell, grey mesh back with headrest, flip-up arms, polished five-star base, v5
  f_0233-f_0244), the 49-inch **curved** monitor (now a flat slab), desk lamp (black architect lamp with domed metal shade,
  f_0238).
- Gable-wall readings (v5 t182-185, t232.5-233.6; poster 36 x 24 in): slopes 35.5 +/- 1.5 deg both sides, flat strip
  0.80, apex 2.12, rear knee / apex 0.58. Loft door step 0.24 +/- 0.03 (v13 t48) against 0.27 - floor stays 6.49.

## (c) New footage

- **v12** (PXL_20261121_125633444): the hatches open and closed and the room around them (f1-14, f43-80, f118-122).
- v13 t48 (loft door from the second-floor platform).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The rear slope is steeper. Ceiling plane `rear_slope` changed from c0 11.7147, cy -0.57735 to c0 12.33, cy -0.70, so
  z is 7.745 at y 6.55 (it was 7.933). `flat` now ends at y 5.31 east of x 1.25. These items on the rear wall and the
  lobby-return wall now cut into the slope:
  - `loft_office.tv` (x 1.25..1.293, y 5.46..6.57, z 7.24..7.88) and `loft_office.tv.picture`: the top rear corner is
    0.15 into the slope (visible in `build/preview/loft_office_tv_r3gate.jpg`)
  - `loft_office.tv_frame.1` (y 5.86..6.10, z 7.91..8.14): 0.08 into it
  - `loft_office.east_frame.0` (x 4.27..4.30, y 5.52..5.90, z 7.99..8.25): 0.05 into it
  - `loft_office.cert.0`..`.3` (x 2.62..4.18, y 6.56..6.59, z 7.30..7.78), on the rear knee wall (now 1.23 high, top
    7.72): the tops are 0.06 into it

  Lower or shrink them to fit under the new slope, z = 12.33 - 0.70 y.
- The top of `loft_office.cabinet` (8.608) now meets the envelope's roof slab, which runs 1 cm above the ceiling, at
  y 5.34..5.38. It is hidden; cosmetic only.
- `h_eaves_front_e` moved to x 1.955..3.005 (centre 2.48). Its swing is clear: the nearest furniture is the coffee
  table at x 0.95..1.95, y 3.15..3.65.
